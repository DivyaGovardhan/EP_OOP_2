from django.urls import path
from .views import (
    RegisterView,
    LogoutUserView,
    LoginUserView,
    CreateApplicationView,
    AccountListView,
    HomepageListView,
    AppDelete
)

urlpatterns = [
    path('', HomepageListView.as_view(), name='index'),
    path('register/', RegisterView.as_view(), name='register'),  # Updated to use RegisterView
    path('logout/', LogoutUserView.as_view(), name='logout'),  # Updated to use LogoutUserView
    path('login/', LoginUserView.as_view(), name='login'),  # Updated to use LoginUserView
    path('create/', CreateApplicationView.as_view(), name='create_app'),  # Updated to use CreateApplicationView
    path('account/', AccountListView.as_view(), name='account'),
    path('app/<int:pk>/delete/', AppDelete.as_view(), name='app_delete'),
]
