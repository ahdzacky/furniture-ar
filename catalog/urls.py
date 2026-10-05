from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('collection/', views.collection_view, name='collection'),
    path('furniture/<int:pk>/', views.furniture_detail, name='furniture_detail'),
]
