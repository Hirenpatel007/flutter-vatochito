from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def api_root(request):
    return JsonResponse({
        "message": "Vatochito Chat API",
        "version": "1.0.0",
        "endpoints": {
            "admin": "/admin/",
            "api_docs": "/api/docs/",
            "api_schema": "/api/schema/",
            "auth": "/api/auth/",
            "chat": "/api/chat/",
        }
    })


urlpatterns = [
    path("", api_root, name="api-root"),
    path("api/", api_root, name="api-root-explicit"),  # Add explicit API root
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/auth/", include("accounts.urls")),
    path("api/chat/", include("chat.urls")),
]

# Serve media files in production (handled by Whitenoise)
if settings.DEBUG or True:  # Always serve media files for now
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
