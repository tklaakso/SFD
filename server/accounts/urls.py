from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup),
    path('delete/', views.delete),
    path('login/', views.login_view),
    path('logout/', views.logout_view),
    path('session/', views.session_view),
    path('whoami/', views.whoami_view),
]