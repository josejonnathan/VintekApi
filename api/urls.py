
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include




urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('', include('api_operations.urls')),
    path('auth/', include('rest_framework.urls')),
    path('messages/', include('user_messages.urls')),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
