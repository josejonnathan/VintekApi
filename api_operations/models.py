from django.db import models
from django.contrib.auth.models import AbstractUser


# Define a custom user model that inherits from AbstractUser
class CustomUser(AbstractUser):
    # Pass is used when there are no additional fields to add
    pass

    # Override the save method
    def save(self, *args, **kwargs):
        # Check if this is a new user (i.e., if the user doesn't have a primary key yet)
        is_new = not self.pk

        # Call the original save method, which saves the user to the database
        super().save(*args, **kwargs)

        # If this is a new user, create a UserProfile for them
        if is_new:
            UserProfile.objects.create(user=self)
            
            
class UserProfile(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    country = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=20, blank=True, null=True)
    adress = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(
    upload_to='profile_pictures/', blank=True, null=True)
    wishlist = models.ManyToManyField('Product', blank=True)

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(default='Default description')
    image = models.ImageField(upload_to='category_images/', null=True)
    


    def __str__(self):
        return self.name


class ProductCondition(models.TextChoices):
    EXCELLENT = 'Excellent'
    VERY_GOOD = 'Very Good'
    GOOD = 'Good'
    ACCEPTABLE = 'Acceptable'
    AS_IS = 'As-Is'


class Product(models.Model):
    name = models.CharField(max_length=50)
    brand = models.CharField(max_length=50, blank=True, null=True)
    model = models.CharField(max_length=50, blank=True, null=True)
    produced_year = models.PositiveIntegerField(blank=True, null=True)
    country_of_origin = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    keywords = models.CharField(max_length=1000, blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, blank=True, null=True)
    condition = models.CharField(
        max_length=20,
        choices=ProductCondition.choices,
        default=ProductCondition.GOOD,
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    publishing_date = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField()
    image = models.ImageField(
        upload_to='product_images/', blank=True, null=True)

    def __str__(self):
        return self.name


class CartStatus(models.TextChoices):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'
    ORDERED = 'Ordered'


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    cart = models.ForeignKey('ShoppingCart', on_delete=models.CASCADE, related_name='items')

    def __str__(self):
        return f'{self.product.name} - {self.quantity}'

class ShoppingCart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=CartStatus.choices,
        default=CartStatus.ACTIVE)

    def __str__(self):
        return f'{self.user.username} - {self.status}'





class OrderStatus(models.TextChoices):
    PENDING = 'Pending'
    SHIPPED = 'Shipped'
    DELIVERED = 'Delivered'
    CANCELLED = 'Cancelled'


class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
    )

    def __str__(self):
        return f'{self.user.username} - {self.order_date}'

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.order.id} - {self.product.name}'
    
# signal to send email notification when an OrderProduct instance is created

@receiver(post_save, sender=OrderProduct)
def notify_owner(sender, instance, created, **kwargs):
    if created:  # Check if the instance was created
        product_owner = instance.product.user
        buyer = instance.order.user
        shipping_address = instance.order.shipping_address
        # Create email subject and body
        subject = f'Your product "{instance.product.name}" has been sold'
        text_content = f'Your product "{instance.product.name}" has been sold to {buyer.username}.'
        html_content = f'''
        <p>Dear {product_owner.username},</p>
        <p>Your product "<strong>{instance.product.name}</strong>" has been sold to <strong>{buyer.username} {buyer.last_name}</strong> ({buyer.email}).</p>
        <p>Quantity: {instance.quantity}</p>
        <p>Total Price: {instance.price * instance.quantity}</p>
        <p>Shipping Address: {shipping_address}</p>
        <p>Thank you for using Vintek</p>
        '''
        # Create email message
        msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [product_owner.email])
        msg.attach_alternative(html_content, "text/html")
        # Send email
        msg.send()
        
        
class PaymentMethod(models.TextChoices):
    CREDIT_CARD = 'Credit Card'
    PAYPAL = 'Paypal'
    BANK_TRANSFER = 'Bank Transfer'


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CREDIT_CARD,
    )
    payment_status = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.order.id} - {self.amount}'