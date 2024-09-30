"""
URL configuration for XEventsAdmin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/edit/<str:user_id>/', views.user_edit, name='user_edit'),
    path('users/delete/<str:user_id>/', views.user_delete, name='user_delete'),
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/create/', views.inventory_create, name='inventory_create'),
    path('inventory/edit/<str:inventory_id>/', views.inventory_edit, name='inventory_edit'),
    path('inventory/delete/<str:inventory_id>/', views.inventory_delete, name='inventory_delete'),
    path('category/create/', views.category_create, name='category_create'),
    path('category/edit/<str:category_id>/', views.category_edit, name='category_edit'),
    path('category/delete/<str:category_id>/', views.category_delete, name='category_delete'),
    path('places/', views.places_list, name='places_list'),
    path('place/create/', views.places_create, name='places_create'),
    path('place/edit/<str:place_id>/', views.places_edit, name='places_edit'),
    path('place/delete/<str:place_id>/', views.places_delete, name='places_delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)