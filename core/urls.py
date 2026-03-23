"""URL configuration for core project."""
 
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('auth_app.api.urls')),
    path('django-rq/', include('django_rq.urls')),
    path('api/', include('content_app.api.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)