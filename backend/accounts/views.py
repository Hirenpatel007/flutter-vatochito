from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserSettings
from .serializers import (
    AuthTokenSerializer, 
    LoginSerializer, 
    RegisterSerializer, 
    UserSerializer,
    ProfileSerializer,
    UserSettingsSerializer
)

User = get_user_model()


class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Exclude the current user from the list
        return User.objects.exclude(id=self.request.user.id)

    @action(detail=False, methods=["get"])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="set-online")
    def set_online(self, request):
        request.user.is_online = True
        request.user.last_seen_at = timezone.now()
        request.user.save(update_fields=["is_online", "last_seen_at"])
        return Response({"status": "online"})

    @action(detail=False, methods=["post"], url_path="set-offline")
    def set_offline(self, request):
        request.user.is_online = False
        request.user.last_seen_at = timezone.now()
        request.user.save(update_fields=["is_online", "last_seen_at"])
        return Response({"status": "offline"})


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request):
        """Register a new user"""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create user with validated data
        user = User.objects.create_user(
            username=serializer.validated_data.get("username"),
            email=serializer.validated_data.get("email", ""),
            password=serializer.validated_data.get("password"),
            display_name=serializer.validated_data.get("display_name", ""),
            phone_number=serializer.validated_data.get("phone_number"),
        )
        
        # Generate JWT tokens for the new user
        refresh = RefreshToken.for_user(user)
        user_serializer = UserSerializer(user)
        
        return Response(
            {
                "user": user_serializer.data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        """Login user and return tokens"""
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        
        # Update user online status
        user.is_online = True
        user.last_seen_at = timezone.now()
        user.save(update_fields=["is_online", "last_seen_at"])
        
        refresh = RefreshToken.for_user(user)
        user_serializer = UserSerializer(user)
        
        return Response(
            {
                "user": user_serializer.data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        )

    @action(detail=False, methods=["post"], url_path="refresh")
    def refresh(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token required."}, status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken(refresh_token)
        return Response({"access": str(token.access_token)})

    @action(detail=False, methods=["post"], url_path="logout")
    def logout(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"], url_path="user", permission_classes=[permissions.IsAuthenticated])
    def get_current_user(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["patch"], url_path="user", permission_classes=[permissions.IsAuthenticated])
    def update_user(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ProfileViewSet(viewsets.ViewSet):
    """Profile management endpoints"""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    @action(detail=False, methods=['get'], url_path='me')
    def get_profile(self, request):
        """Get current user's profile"""
        serializer = ProfileSerializer(request.user, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch', 'put'], url_path='me')
    def update_profile(self, request):
        """Update current user's profile"""
        serializer = ProfileSerializer(
            request.user, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='avatar')
    def upload_avatar(self, request):
        """Upload profile avatar"""
        if 'avatar' not in request.FILES:
            return Response(
                {'error': 'No avatar file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = request.user
        user.avatar = request.FILES['avatar']
        user.save(update_fields=['avatar'])
        
        serializer = ProfileSerializer(user, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['delete'], url_path='avatar')
    def delete_avatar(self, request):
        """Delete profile avatar"""
        user = request.user
        if user.avatar:
            user.avatar.delete()
        user.avatar = None
        user.save(update_fields=['avatar'])
        
        return Response({'message': 'Avatar deleted successfully'})
    
    @action(detail=True, methods=['get'], url_path='view')
    def view_profile(self, request, pk=None):
        """View another user's profile (respects privacy settings)"""
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Build response based on privacy settings
        data = {
            'id': user.id,
            'username': user.username,
            'display_name': user.display_name,
            'status_message': user.status_message,
            'bio': user.bio,
        }
        
        # Show avatar based on privacy
        if user.show_profile_photo:
            data['avatar'] = request.build_absolute_uri(user.avatar.url) if user.avatar else None
        
        # Show phone based on privacy
        if user.show_phone_number:
            data['phone_number'] = user.phone_number
        
        # Show last seen based on privacy
        if user.show_last_seen:
            data['is_online'] = user.is_online
            data['last_seen_at'] = user.last_seen_at
        
        return Response(data)


class SettingsViewSet(viewsets.ViewSet):
    """User settings management"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def get_settings(self, request):
        """Get user settings"""
        settings, created = UserSettings.objects.get_or_create(user=request.user)
        serializer = UserSettingsSerializer(settings)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch', 'put'])
    def update_settings(self, request):
        """Update user settings"""
        settings, created = UserSettings.objects.get_or_create(user=request.user)
        serializer = UserSettingsSerializer(settings, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='reset')
    def reset_settings(self, request):
        """Reset settings to default"""
        settings, created = UserSettings.objects.get_or_create(user=request.user)
        
        # Reset to defaults
        settings.enable_notifications = True
        settings.notification_sound = True
        settings.message_preview = True
        settings.enter_to_send = True
        settings.auto_download_photos = True
        settings.auto_download_videos = False
        settings.auto_download_files = False
        settings.two_factor_enabled = False
        settings.show_typing_indicator = True
        settings.show_read_receipts = True
        settings.theme = 'light'
        settings.font_size = 'medium'
        settings.language = 'en'
        settings.save()
        
        serializer = UserSettingsSerializer(settings)
        return Response(serializer.data)
