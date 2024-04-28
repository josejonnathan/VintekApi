from django.urls import path
from .views import RegisterView
from django.contrib.auth import views as auth_views


from .views import (
    CategoryList,
    ProductList,
    ProductDetail,
    UserProfileDetail,
    CustomUserUpdateView,
    OrderCreateView,
    OrderProductCreateView,
    PaymentProcessView,
    OrderListView,
    OrderDetailView,
    ProductSearchView,
    ShoppingCartViewSet,
    RegisterView,
    LoginView, 
    LogoutView,
    CategoryDetailView,
    ProductCreate,
    WishlistView,
    ClearCartView,
    CategoryProductsList,
    SoldOrdersView
    
)

app_name = 'api_operations'

urlpatterns = [
    #Categories
    path('api/categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('api/categories/', CategoryList.as_view(), name='category_list'),
    path('api/categories/<int:category_id>/products/', CategoryProductsList.as_view(), name='category-products'),
    
     #Products
    path('api/products/create/', ProductCreate.as_view(), name='product_create'),
    path('api/products/', ProductList.as_view(), name='product_list'),
    path('api/products/<int:pk>/', ProductDetail.as_view(), name='product_detail'),
    # path('api/products/unique-products/', UniqueProductList.as_view(), name='unique-product-list'),
    path('api/products/search/', ProductSearchView.as_view(), name='product_search'),
    
    #Wishlist
    path('api/wishlist/', WishlistView.as_view(), name='wishlist'),

    #Users_Profile
    path('api/users/<int:pk>/', UserProfileDetail.as_view(), name='user_detail'),
    path('user/<int:pk>/', CustomUserUpdateView.as_view(), name='user_update'),

    
    #Authentication    
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    
    #Orders
    path('order/create/', OrderCreateView.as_view(), name='order_create'),
    path('order/product/add/', OrderProductCreateView.as_view(), name='order_product_add'),
    path('api/orders/', OrderListView.as_view(), name='order_list'),
    path('api/orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    
    #Selling
    path('api/sold_orders', SoldOrdersView.as_view(), name='sold_orders'),
    
    #Payments
    path('payment/process/', PaymentProcessView.as_view(), name='payment_process'),
    
    #Shopping Cart
    path('api/shopping-cart/', ShoppingCartViewSet.as_view({'get': 'list'}), name='shoppingcart_list'),
    path('api/shopping-cart/add-product/', ShoppingCartViewSet.as_view({'post': 'add_product'}), name='shoppingcart_add_product'),
    path('api/shopping-cart/<int:pk>/remove-product/', ShoppingCartViewSet.as_view({'delete': 'remove_product'}), name='shoppingcart_remove_product'),
    path('api/shopping-cart/<int:pk>/delete-product/', ShoppingCartViewSet.as_view({'delete': 'delete_product'}), name='shoppingcart_delete_product'),
    path('api/shopping-cart/<int:pk>/increment-product/', ShoppingCartViewSet.as_view({'post': 'increment_product'}), name='shoppingcart_increment_product'),
    path('api/shopping-cart/clear_cart/', ClearCartView.as_view(), name='shoppingcart_clear_cart'),


]