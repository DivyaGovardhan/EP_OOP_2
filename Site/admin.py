from django.contrib import admin
from .models import User, DesignApplication, Category

admin.site.register(User)
admin.site.register(DesignApplication)
admin.site.register(Category)