from rest_framework import serializers
from .models import (
    CustomUser,
    UserProfile,
    Category,
    Product,
    ProductCondition,
    CartStatus,
    ShoppingCart,
    OrderStatus,
    Order,
    OrderProduct,
    PaymentMethod,
    Payment,
    CartItem,
    
)
from django.contrib.auth import get_user_model


# This line retrieves the User model. The get_user_model function is a Django function that retrieves the currently active user model.
User = get_user_model()

# This is a serializer for the User model. It inherits from Django REST Framework's ModelSerializer.
class CustomUserSerializer(serializers.ModelSerializer):
    # This line defines a password field that is write-only and not required.
    password = serializers.CharField(write_only=True, required=False)

    # This is the Meta class for the serializer. It defines the model and fields to be used by the serializer.
    class Meta:
        # The model to be used by the serializer is set to User.
        model = User
        # The fields to be used by the serializer are set to username, email, first name, last name, and password.
        fields = ('username', 'email', 'first_name', 'last_name', 'password')

    # This is the create method for the serializer. It is called when a new instance of the model is created.
    def create(self, validated_data):
        # The password is popped from the validated data.
        password = validated_data.pop('password', None)
        # A new instance of the model is created with the validated data.
        instance = self.Meta.model(**validated_data)
        # If a password was provided, it is set on the instance.
        if password is not None:
            instance.set_password(password)
        # The instance is saved.
        instance.save()
        # The instance is returned.
        return instance

    # This is the update method for the serializer. It is called when an existing instance of the model is updated.
    def update(self, instance, validated_data):
        # The password is popped from the validated data.
        password = validated_data.pop('password', None)
        # The validated data is set on the instance.
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        # If a password was provided, it is set on the instance.
        if password is not None:
            instance.set_password(password)
        # The instance is saved.
        instance.save()
        # The instance is returned.
        return instance

# This is a serializer for the Product model. It inherits from Django REST Framework's ModelSerializer.
class ProductSerializer(serializers.ModelSerializer):
    # This line defines a read-only field that retrieves the name of the category associated with the product.
    category_name = serializers.CharField(source='category.name', read_only=True)
    # This line includes the CustomUserSerializer in the ProductSerializer.
    user = CustomUserSerializer()

    # This is the Meta class for the serializer. It defines the model and fields to be used by the serializer.
    class Meta:
        # The model to be used by the serializer is set to Product.
        model = Product
        # The fields to be used by the serializer are set.
        fields = ['id', 'name', 'brand', 'model', 'produced_year', 'country_of_origin', 'description', 'keywords', 'condition', 'price', 'publishing_date', 'quantity', 'image', 'category', 'user', 'category_name']


class UserProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    wishlist = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'country', 'city', 'adress', 'phone_number', 'profile_picture', 'user', 'wishlist']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    user = CustomUserSerializer()  # Include the CustomUserSerializer in the ProductSerializer

    class Meta:
        model = Product
        fields = ['id', 'name', 'brand', 'model', 'produced_year', 'country_of_origin', 'description', 'keywords', 'condition', 'price', 'publishing_date', 'quantity', 'image', 'category', 'user', 'category_name']


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__' 
        
        

class ProductConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCondition
        fields = '__all__'
        
        

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    user = serializers.ReadOnlyField(source='product.user.username')

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'user']


class ShoppingCartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = ShoppingCart
        fields = '__all__'


class OrderProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    buyer_username = serializers.ReadOnlyField(source='order.user.username')

    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity', 'price', 'order', 'buyer_username']
        
        

class OrderSerializer(serializers.ModelSerializer):
    orderproduct_set = OrderProductSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'total_price', 'shipping_address', 'order_date', 'status', 'orderproduct_set']



class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'


class CartStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartStatus
        fields = '__all__'


class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = '__all__'


class ProductConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCondition
        fields = '__all__'
