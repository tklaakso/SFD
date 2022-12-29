from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create, name='create'),
    path('delete/', views.delete),
    path('view/', views.view, name='view'),
    path('browse/', views.browse),
    path('menu/', views.menu),
]