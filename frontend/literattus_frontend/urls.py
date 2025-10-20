"""
URL configuration for Literattus frontend.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Core app (home, landing)
    path('', include('apps.core.urls')),
    
    # Authentication
    path('auth/', include('apps.users.urls')),
    
    # Books
    path('books/', include('apps.books.urls')),
    
    # Clubs
    path('clubs/', include('apps.clubs.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

