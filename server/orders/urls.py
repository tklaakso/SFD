from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add, name='add'),
    path('remove/', views.remove, name='remove'),
    path('cart/', views.cart, name='cart'),
    path('place/', views.place, name='place'),
    path('cancel/', views.cancel, name='cancel'),
    path('view_all/', views.view_all, name='view_all'),
    path('reset/', views.reset, name='reset'),
]