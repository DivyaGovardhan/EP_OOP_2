from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('superadmin/', admin.site.urls),
    path('design/', include('Site.urls')),
    path('catalog/', RedirectView.as_view(url='', permanent=True)),
    path('', RedirectView.as_view(url='/design/', permanent=True)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
