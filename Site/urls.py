from django.urls import path
from .views import (
    HomepageListView,
    RegisterView,
    LoginUserView,
    LogoutUserView,
    AccountListView,
    CreateApplicationView, AppsListView, RedactApp, AppDelete,
    CreateCategory, CategoriesListView, RedactCategory, CategoryDelete,
)

urlpatterns = [
    path('', HomepageListView.as_view(), name='index'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutUserView.as_view(), name='logout'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('account/', AccountListView.as_view(), name='account'),
    path('create-app/', CreateApplicationView.as_view(), name='create_app'),
    path('apps-list/', AppsListView.as_view(), name='apps_list'),
    path('app/<int:pk>/redact/', RedactApp.as_view(), name='redact_app'),
    path('app/<int:pk>/delete/', AppDelete.as_view(), name='app_delete'),
    path('category/create/', CreateCategory.as_view(), name='create_categ'),
    path('categ-list/', CategoriesListView.as_view(), name='categ_list'),
    path('category/<int:pk>/redact/', RedactCategory.as_view(), name='redact_categ'),
    path('category/<int:pk>/delete/', CategoryDelete.as_view(), name='delete_categ'),
]
