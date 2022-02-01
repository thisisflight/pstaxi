import debug_toolbar
from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('main.urls')),
    path('admin/', admin.site.urls),
    path('motorpool/', include('motorpool.urls')),
    path('accounts/', include('accounts.urls')),
    path('allauth/accounts/', include('allauth.urls')),
    path('__debug__/', include(debug_toolbar.urls))
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
