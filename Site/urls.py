from django.urls import path
from .views import register, logout_user, login_user, create_application, AccountListView, HomepageListView, AppDelete
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', HomepageListView.as_view(), name='index'),
    path('register/', register, name='register'),
    path('logout/', logout_user, name='logout'),
    path('login/', login_user, name='login'),
    path('create/', create_application, name='create_app'),
    path('account/', AccountListView.as_view(), name='account'),
    path('app/<int:pk>/delete/', AppDelete.as_view(), name='app_delete'),
]