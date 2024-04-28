from django.contrib import admin
from .models import (CustomUser, UserProfile, Category, Product, Payment, ShoppingCart,Order,OrderProduct)


admin.site.register(CustomUser)
admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ShoppingCart)
admin.site.register(Order)
admin.site.register(OrderProduct)
admin.site.register(Payment)

