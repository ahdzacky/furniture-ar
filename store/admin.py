from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from .models import Cart, CartItem, Order, OrderItem, ShippingAddress, UserProfile


class CartItemInline(TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('furniture', 'quantity', 'variant')


@admin.register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ('user', 'get_item_count', 'get_total', 'created_at')
    readonly_fields = ('user', 'created_at')
    inlines = [CartItemInline]


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('furniture_name', 'price', 'quantity', 'variant_name', 'get_subtotal')


class ShippingAddressInline(StackedInline):
    model = ShippingAddress
    extra = 0
    readonly_fields = ('full_name', 'phone', 'address', 'city', 'province', 'postal_code')


@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    list_display = ('user', 'phone', 'city', 'province')
    search_fields = ('user__username', 'user__email', 'phone')

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'payment_method', 'formatted_total', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__email')
    list_editable = ('status',)
    readonly_fields = ('order_number', 'user', 'total_price', 'created_at', 'updated_at')
    inlines = [ShippingAddressInline, OrderItemInline]
    ordering = ('-created_at',)
