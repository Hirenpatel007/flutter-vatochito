from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AuthViewSet, UserViewSet, ProfileViewSet, SettingsViewSet

# Import real auth views (lazy import to avoid errors if packages not installed)
try:
    from . import auth_views as real_auth
    REAL_AUTH_AVAILABLE = True
except ImportError:
    REAL_AUTH_AVAILABLE = False

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")

auth_views = AuthViewSet.as_view({
    "post": "create",  # For registration
})

auth_login = AuthViewSet.as_view({
    "post": "login",
})

auth_logout = AuthViewSet.as_view({
    "post": "logout",
})

auth_user = AuthViewSet.as_view({
    "get": "get_current_user",
    "patch": "update_user",
})

auth_refresh = AuthViewSet.as_view({
    "post": "refresh",
})

# Profile views
profile_me = ProfileViewSet.as_view({
    "get": "get_profile",
    "patch": "update_profile",
    "put": "update_profile",
})

profile_avatar = ProfileViewSet.as_view({
    "post": "upload_avatar",
    "delete": "delete_avatar",
})

profile_view = ProfileViewSet.as_view({
    "get": "view_profile",
})

# Settings views
settings_view = SettingsViewSet.as_view({
    "get": "get_settings",
    "patch": "update_settings",
    "put": "update_settings",
})

settings_reset = SettingsViewSet.as_view({
    "post": "reset_settings",
})

urlpatterns = [
    path("", include(router.urls)),
    path("register/", auth_views, name="register"),
    path("login/", auth_login, name="login"),
    path("logout/", auth_logout, name="logout"),
    path("user/", auth_user, name="current-user"),
    path("token/refresh/", auth_refresh, name="token-refresh"),
    
    # Profile endpoints
    path("profile/me/", profile_me, name="profile-me"),
    path("profile/avatar/", profile_avatar, name="profile-avatar"),
    path("profile/<int:pk>/", profile_view, name="profile-view"),
    
    # Settings endpoints
    path("settings/", settings_view, name="settings"),
    path("settings/reset/", settings_reset, name="settings-reset"),
]

# Add real authentication endpoints - always add them
# The views themselves will handle missing dependencies gracefully
if REAL_AUTH_AVAILABLE:
    urlpatterns += [
        # Phone OTP Authentication
        path("phone/request-otp/", real_auth.request_phone_otp, name="phone-request-otp"),
        path("phone/verify-otp/", real_auth.verify_phone_otp, name="phone-verify-otp"),
        
        # Google OAuth Authentication
        path("google/", real_auth.google_auth, name="google-auth"),
        
        # Logout endpoint
        path("auth/logout/", real_auth.logout, name="auth-logout"),
    ]
else:
    # If real auth not available, log the error
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Real authentication endpoints (Phone OTP, Google OAuth) are NOT available. Install required packages: google-auth, twilio, phonenumberslite")
