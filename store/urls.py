from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Checkout & Orders
    path('checkout/', views.checkout_view, name='checkout'),
    path('checkout/success/', views.order_success, name='order_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('my-orders/<str:order_number>/', views.order_detail, name='order_detail'),
    path('my-orders/<str:order_number>/cancel/', views.cancel_order, name='cancel_order'),
    path('webhook/xendit/', views.xendit_webhook, name='xendit_webhook'),

    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/password/', views.password_change_view, name='password_change'),
]
