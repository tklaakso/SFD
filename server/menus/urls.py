from django.urls import path
from . import views

urlpatterns = [
    path('view/', views.view),
    path('add/', views.add),
    path('modify/', views.modify),
    path('remove/', views.remove),
]