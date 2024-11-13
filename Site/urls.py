from django.urls import path, include
from .views import register, index, logout_user, login_user

urlpatterns = [
    path('', index, name='index'),
    path('register/', register, name='register'),
    path('logout/', logout_user, name='logout'),
    path('login/', login_user, name='login'),
]