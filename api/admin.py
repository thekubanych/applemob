from django.contrib import admin
from .models import *

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'order')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'card_price', 'in_stock')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'created_at')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('address', 'working_hours')

admin.site.register(Promotion)
admin.site.register(Address)
admin.site.register(BonusCard)
admin.site.register(Notification)
admin.site.register(CartItem)
admin.site.register(Favorite)