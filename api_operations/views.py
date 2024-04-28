from django.db import transaction
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import ShoppingCart, CartItem, Product
from .serializers import ShoppingCartSerializer, CartItemSerializer
from rest_framework import generics
from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
import django_filters
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework.generics import RetrieveAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from .permissions import IsOrderOwner, IsShoppingCartOwner, IsUserProfileOwner, IsProductOwnerOrReadOnly, IsCustomUserOwner
from rest_framework.permissions import IsAuthenticated, AllowAny
# hypothetical payment processor module
from .payment_processor import process_payment
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from .models import Order, Product, OrderProduct
from rest_framework import viewsets
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import (
    Product,
    UserProfile,
    OrderProduct,
    Order,
    ShoppingCart,
    Category,
    CartItem,
    OrderStatus
)

from .serializers import (
    ProductSerializer,
    UserProfileSerializer,
    CustomUserSerializer,
    OrderSerializer,
    ShoppingCartSerializer,
    CategorySerializer,
    CartItemSerializer,
    OrderProductSerializer,


)

# -------------------PRODUCT------------------------------------------------------------------------------------------------------------------------


class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = ['category', 'name', 'price', 'brand', 'model', 'produced_year',
                  'country_of_origin', 'description', 'keywords', 'condition', 'user']
        filter


class ProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter,]
    search_fields = ['category', 'name', 'price', 'brand', 'model', 'produced_year',
                     'country_of_origin', 'description', 'keywords', 'condition', 'user']
    filterset_class = ProductFilter
    
    
class ProductCreate(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    parser_classes = (MultiPartParser, FormParser)  # Add parsers for handling file uploads
    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [AllowAny]
        return super(ProductCreate, self).get_permissions()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAuthenticated, IsProductOwnerOrReadOnly]
        else:
            self.permission_classes = [AllowAny]
        return super(ProductDetail, self).get_permissions()

    def retrieve(self, request, *args, **kwargs):
        try:
            response = super().retrieve(request, *args, **kwargs)
            user_id = request.session.get('user_id')
            if user_id:
                response.data['is_owner'] = user_id == response.data['user']
            return response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        print("Incoming request data:", request.data)  # Print the incoming request data
        try:
            response = super().update(request, *args, **kwargs)
            print("Data sent in PUT request:", response.data)  # Print the data sent in the PUT request
            return response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class ProductSearchView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        query = self.request.query_params.get('search', None)
        if query:
            queryset = Product.objects.filter(Q(name__icontains=query))
            if not queryset:
                raise Http404("Not Found")
        else:
            raise Http404("No search query provided.")
        return queryset
    
#-------------Category------------------------------------------------------------------------------------------------------------------------

class CategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    

class CategoryDetailView(RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    

class CategoryProductsList(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Product.objects.filter(category_id=category_id)
    
    
# -----------------------USER-------------------------------------------------------------------------------------------------------------------------

User = get_user_model()


class CustomUserUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs.get('pk')
        return get_object_or_404(UserProfile, user__id=user_id)


class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'Please provide both username and password'},
                status=status.HTTP_400_BAD_REQUEST
            )

        existing_user = User.objects.filter(username=username).first()
        if existing_user:
            return Response(
                {'error': 'Username already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(username=username, password=password)
        # create a UserProfile for the new user
        UserProfile.objects.create(user=user)

        token = Token.objects.create(user=user)

        return Response({'token': str(token)}, status=status.HTTP_201_CREATED)

    permission_classes = [permissions.IsAuthenticated, IsUserProfileOwner]


# -------------------ORDER-----------------------------------------------------------------------------------------------------------------------------

class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderProductCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        product_id = request.data.get('product_id')
        order_id = request.data.get('order_id')
        quantity = request.data.get('quantity')
        price = request.data.get('price') 
    
        if not product_id or not order_id:
            return Response({'message': 'Product ID and Order ID are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
            order = Order.objects.get(id=order_id, user=user)
        except ObjectDoesNotExist:
            return Response({'message': 'Product or Order not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if there's enough quantity in stock
        if product.quantity < quantity:
            return Response({'message': 'Not enough quantity in stock'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                order_product = OrderProduct.objects.create(order=order, product=product, quantity=quantity, price=price)
                
                # Reduce the quantity of the product
                product.quantity -= quantity
                product.save()
        except Exception as e:
            return Response({'message': 'Failed to add product to order', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

        return Response({
            'message': 'Product added to order',
            'order_product': {
                'id': order_product.id,
                'order_id': order_product.order.id,
                'product_id': order_product.product.id,
                'quantity': order_product.quantity,
                'price': order_product.price, 
            },
        }, status=status.HTTP_201_CREATED)


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer

    permission_classes = [permissions.IsAuthenticated, IsOrderOwner]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user)


from rest_framework.response import Response

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.filter(user=user)
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
        
        
class SoldOrdersView(generics.ListAPIView):
    serializer_class = OrderProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return OrderProduct.objects.filter(product__user=user)
    
    
    

@method_decorator(csrf_exempt, name='dispatch')
class OrderView(View):
    def delete(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            order.delete()
            return JsonResponse({'message': 'Order deleted'}, status=200)
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)
        

# -------------------PAYMENT--------------------------------------------------------------------------------------------------------------------
class PaymentProcessView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOrderOwner]

    def post(self, request):
        user = request.user
        order_id = request.data.get('order_id')
        # payment info from the front-end
        payment_info = request.data.get('payment_info')

        # Validate inputs
        if not order_id or not payment_info:
            return Response({'error': 'Invalid input'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id, user=user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            with transaction.atomic():
                # Include the amount in the payment_info
                payment_info['amount'] = order.total_price  

                # Process the payment
                payment_result = process_payment(payment_info)

                # update order status
                if payment_result['success']:
                    order.status = OrderStatus.SHIPPED
                    order.save()
                    return Response({'message': 'Payment processed'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': payment_result['message']}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -------------------SHOPPING CART API----------------------------------------------------------------------------------------------------------------------

class ShoppingCartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    

    def list(self, request):
        cart = ShoppingCart.objects.filter(user=request.user).first()
        if cart is None:
            return Response({'error': 'No shopping cart found for this user.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ShoppingCartSerializer(cart)
        response = serializer.data
        response['items'] = CartItemSerializer(cart.items.all(), many=True).data
        return Response(response)

    @action(detail=False, methods=['post'])
    def add_product(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)  # Default to 1 if no quantity is provided
        product = get_object_or_404(Product, pk=product_id)
        cart, created = ShoppingCart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(product=product, cart=cart, defaults={'quantity': quantity})
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        return Response({"message": "Product added to cart"}, status=200)

    @action(detail=True, methods=['delete'])
    def remove_product(self, request, pk=None):
        cart_item = CartItem.objects.filter(id=pk, cart__user=request.user).first()
        if cart_item is None:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            cart_item.delete()
            return Response({'message': 'Product removed from cart'}, status=status.HTTP_204_NO_CONTENT)
        
        
    @action(detail=True, methods=['post'])
    def increment_product(self, request, pk=None):
        cart_item = CartItem.objects.filter(id=pk, cart__user=request.user).first()
        if cart_item is None:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the quantity exceeds the available stock
        if cart_item.product.quantity < cart_item.quantity + 1:
            return Response({
                'error': 'Not enough product available',
                'message': f'You cannot add more than {cart_item.product.quantity} of this product'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        cart_item.quantity += 1
        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    @action(detail=True, methods=['delete'])
    def delete_product(self, request, pk=None):
        cart_item = CartItem.objects.filter(id=pk, cart__user=request.user).first()
        if cart_item is not None:
            cart_item.delete()
            return Response({'message': 'Product removed from cart'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'Product not found in cart'}, status=status.HTTP_400_BAD_REQUEST)


class ClearCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        cart = ShoppingCart.objects.filter(user=request.user).first()
        if cart is not None:
            cart.items.all().delete()  # Use items instead of cartitem_set
            return Response({'message': 'Shopping cart cleared'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'Shopping cart not found'}, status=status.HTTP_404_NOT_FOUND)
# -------------------REGISTER AND LOGIN-LOGOUT-----------------------------------------------------------------------------------------------------------------------------


User = get_user_model()


class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        if not username or not password or not email or not first_name or not last_name:
            return Response(
                {'error': 'Please provide all required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )

        existing_user = User.objects.filter(username=username).first()
        if existing_user:
            return Response(
                {'error': 'Username already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            username=username, password=password, email=email, first_name=first_name, last_name=last_name)
        token = Token.objects.create(user=user)

        return Response({'token': str(token)}, status=status.HTTP_201_CREATED)


User = get_user_model()


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'Please provide both username and password'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {'error': 'Invalid username or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        # Log the user in. This will create a session for the user.
        login(request, user)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': str(token), 'user_id': user.id, 'username': username}, status=status.HTTP_200_OK)



class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully'}, status=200)


# -------------------Wishlist-----------------------------------------------------------------------------------------------------------------------------


class WishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        userprofile = request.user.userprofile_set.first()
        if userprofile:
            wishlist = userprofile.wishlist.all()
            serializer = ProductSerializer(wishlist, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'User has no profile'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        product_id = request.data.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        userprofile = request.user.userprofile_set.first()
        if userprofile:
            userprofile.wishlist.add(product)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'User has no profile'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        product_id = request.data.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        userprofile = request.user.userprofile_set.first()
        if userprofile:
            userprofile.wishlist.remove(product)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'User has no profile'}, status=status.HTTP_404_NOT_FOUND)