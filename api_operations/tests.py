from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import encode_multipart
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Product, CustomUser, UserProfile, Order, OrderStatus, ShoppingCart, CartItem
from api_operations.models import Category, CustomUser
import json

class ProductListTestCase(TestCase):
        
    def setUp(self):
        self.client = APIClient()
        # Create a user for testing
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')
        # Create a few products for testing
        Product.objects.create(name='Product 1', price=10, quantity=5, user=self.user)
        Product.objects.create(name='Product 2', price=20, quantity=10, user=self.user)
        
    def test_product_list(self):
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        
        
class ProductCreateTestCase(APITestCase):
    def setUp(self):
        # Create a user and authenticate the test client
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create a Category object
        self.category = Category.objects.create(name='Category 1')

    def test_product_create(self):
        data = {
            'name': 'Product 1',
            'brand': 'Brand 1',
            'model': 'Model 1',
            'produced_year': 2020,
            'country_of_origin': 'Country 1',
            'description': 'Description 1',
            'keywords': 'Keywords 1',
            'condition': 'Very Good',  
            'price': 10,
            'publishing_date': '2022-01-01',
            'quantity': 5,
            'category': self.category.id,
            'user': self.user.id,  # Include the user field
        }
    
        url = reverse('api_operations:product_create')
        response = self.client.post(url, data)
        print(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.get().name, 'Product 1')
        
class UserAccountTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_model = get_user_model()

    def test_register(self):
        response = self.client.post(reverse('api_operations:register'), json.dumps({
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'testuser@example.com',
            'first_name': 'Test',
            'last_name': 'User',
        }), content_type='application/json')
        self.assertEqual(response.status_code, 201)  # Created
        users = self.user_model.objects.all()
        self.assertEqual(users.count(), 1)
        self.assertEqual(users[0].username, 'testuser')

    def test_login(self):
        self.user_model.objects.create_user(username='testuser', password='testpass123')
        response = self.client.post(reverse('api_operations:login'), json.dumps({
            'username': 'testuser',
            'password': 'testpass123',
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)  # OK

    def test_logout(self):
        self.user_model.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('api_operations:logout'), content_type='application/json')
        self.assertEqual(response.status_code, 200)  # OK
        
        
class OrderTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(username='testuser', password='testpass123')
        self.token = Token.objects.create(user=self.user)
        self.product = Product.objects.create(name='Test Product', price=100, quantity=10, user=self.user)
        self.order = Order.objects.create(user=self.user, total_price=100)

    def test_order_create(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token))
        response = self.client.post(reverse('api_operations:order_create'), json.dumps({
            'user': self.user.id,
            'shipping_address': '123 Test St',
            'total_price': 200,
        }), content_type='application/json')
        print(response.data)  # Print the response data
        self.assertEqual(response.status_code, 201)  # Created

    def test_order_list(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token))
        response = self.client.get(reverse('api_operations:order_list'))
        self.assertEqual(response.status_code, 200)  # OK
        self.assertEqual(len(response.data), 1)

    def test_order_detail(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token))
        response = self.client.get(reverse('api_operations:order_detail', kwargs={'pk': self.order.id}))
        self.assertEqual(response.status_code, 200)  # OK
        self.assertEqual(response.data['id'], self.order.id)
        

class ShoppingCartTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(username='testuser', password='testpass123')
        self.token = Token.objects.create(user=self.user)
        self.product = Product.objects.create(name='Test Product', price=100, quantity=10, user=self.user)
        self.cart = ShoppingCart.objects.create(user=self.user)

    def test_add_product(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token))
        response = self.client.post(reverse('api_operations:shoppingcart_add_product'), json.dumps({
            'product_id': self.product.id,
            'quantity': 1,
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)  # OK
        cart_items = CartItem.objects.filter(cart=self.cart)
        self.assertEqual(cart_items.count(), 1)

    def test_remove_product(self):
        cart_item = CartItem.objects.create(product=self.product, cart=self.cart, quantity=1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token))
        response = self.client.delete(reverse('api_operations:shoppingcart_remove_product', kwargs={'pk': cart_item.id}))
        self.assertEqual(response.status_code, 204)  
        cart_items = CartItem.objects.filter(cart=self.cart)
        self.assertEqual(cart_items.count(), 0)

    def test_increment_product(self):
        cart_item = CartItem.objects.create(product=self.product, cart=self.cart, quantity=1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token))
        response = self.client.post(reverse('api_operations:shoppingcart_increment_product', kwargs={'pk': cart_item.id}))
        self.assertEqual(response.status_code, 200)  # OK
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 2)

    def test_clear_cart(self):
        CartItem.objects.create(product=self.product, cart=self.cart, quantity=1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token))
        response = self.client.delete(reverse('api_operations:shoppingcart_clear_cart'))
        self.assertEqual(response.status_code, 204)  
        cart_items = CartItem.objects.filter(cart=self.cart)
        self.assertEqual(cart_items.count(), 0)
        
        
class WishlistTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(username='testuser', password='testpass123')
        self.token = Token.objects.create(user=self.user)
        self.product = Product.objects.create(name='Test Product', price=100, quantity=10, user=self.user)
        self.user_profile = self.user.userprofile_set.first()  # Retrieve the user profile

    def test_add_product_to_wishlist(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token))
        response = self.client.post(reverse('api_operations:wishlist'), json.dumps({
            'product_id': self.product.id,
        }), content_type='application/json')
        self.assertEqual(response.status_code, 204)  
        self.user_profile.refresh_from_db()  

    def test_remove_product_from_wishlist(self):
        self.user_profile.wishlist.add(self.product)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token))
        response = self.client.delete(reverse('api_operations:wishlist'), json.dumps({
            'product_id': self.product.id,
        }), content_type='application/json')
        self.assertEqual(response.status_code, 204)  
        self.user_profile.refresh_from_db()  
        self.assertFalse(self.product in self.user_profile.wishlist.all())

    def test_get_wishlist(self):
        self.user_profile.wishlist.add(self.product)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.token))
        response = self.client.get(reverse('api_operations:wishlist'))
        self.assertEqual(response.status_code, 200)  # OK
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.product.id)
        

class CategoryTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass123')
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(name='Test Product', price=100, quantity=10, category=self.category, user=self.user)
    def test_category_list(self):
        response = self.client.get(reverse('api_operations:category_list'))
        self.assertEqual(response.status_code, 200)  # OK
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.category.id)

    def test_category_detail(self):
        response = self.client.get(reverse('api_operations:category-detail', kwargs={'pk': self.category.id}))
        self.assertEqual(response.status_code, 200)  # OK
        self.assertEqual(response.data['id'], self.category.id)
    
    def test_category_products_list(self):
        response = self.client.get(reverse('api_operations:category-products', kwargs={'category_id': self.category.id}))
        self.assertEqual(response.status_code, 200)  # OK
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.product.id)
        

class PaymentProcessViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)
        self.order = Order.objects.create(user=self.user, total_price=100, status=OrderStatus.PENDING)
        self.payment_info = {
            'method': 'credit_card',
            'card_number': '4242424242424242',
            'exp_month': 12,
            'exp_year': 2023,
            'cvc': '123'
        }

    def test_payment_process(self):
        data = {
            'order_id': self.order.id,
            'payment_info': self.payment_info
        }
        print(data)
        response = self.client.post(reverse('api_operations:payment_process'), data, format='json')
        print(response.data)
        self.order.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.order.status, OrderStatus.SHIPPED)
        

class UserProfileDetailTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)
        UserProfile.objects.filter(user=self.user).delete()
        self.user_profile = UserProfile.objects.create(user=self.user, country='Test Country', city='Test City')
    def test_get_user_profile_detail(self):
        response = self.client.get(reverse('api_operations:user_detail', kwargs={'pk': self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['country'], 'Test Country')
        self.assertEqual(response.data['city'], 'Test City')

    def test_update_user_profile_detail(self):
        response = self.client.put(reverse('api_operations:user_detail', kwargs={'pk': self.user.id}), {'country': 'Updated Country', 'city': 'Updated City'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['country'], 'Updated Country')
        self.assertEqual(response.data['city'], 'Updated City')

    def test_delete_user_profile_detail(self):
        response = self.client.delete(reverse('api_operations:user_detail', kwargs={'pk': self.user.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)