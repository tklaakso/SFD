from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup),
    path('recommended/', views.recommended),
    path('accept/', views.accept),
    path('decline/', views.decline),
]