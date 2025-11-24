from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, UserSettings


class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = [
            'id', 'enable_notifications', 'notification_sound', 'message_preview',
            'enter_to_send', 'auto_download_photos', 'auto_download_videos', 'auto_download_files',
            'two_factor_enabled', 'show_typing_indicator', 'show_read_receipts',
            'theme', 'font_size', 'language', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    settings = UserSettingsSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "display_name",
            "phone_number",
            "avatar",
            "status_message",
            "bio",
            "is_online",
            "last_seen_at",
            "date_of_birth",
            "country",
            "city",
            "website",
            "show_phone_number",
            "show_last_seen",
            "show_profile_photo",
            "allow_calls",
            "allow_group_invite",
            "settings",
        ]
        read_only_fields = ["id", "is_online", "last_seen_at"]


class ProfileSerializer(serializers.ModelSerializer):
    """Detailed profile serializer with all fields"""
    settings = UserSettingsSerializer(read_only=True)
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "display_name", "phone_number",
            "avatar", "avatar_url", "status_message", "bio",
            "date_of_birth", "country", "city", "website",
            "show_phone_number", "show_last_seen", "show_profile_photo",
            "allow_calls", "allow_group_invite",
            "is_online", "last_seen_at", "date_joined", "settings"
        ]
        read_only_fields = ["id", "is_online", "last_seen_at", "date_joined"]
    
    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
        return None


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8, label="Confirm Password")
    email = serializers.EmailField(required=False, allow_blank=True)
    display_name = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "display_name",
            "phone_number",
            "password",
            "password2",
        ]
    
    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        return attrs


class AuthTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["display_name"] = user.display_name
        return token


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    password = serializers.CharField(style={"input_type": "password"})

    def validate(self, attrs):
        username = attrs.get("username")
        phone_number = attrs.get("phone_number")
        password = attrs.get("password")

        if not username and not phone_number:
            raise serializers.ValidationError("Username or phone number is required.")

        credentials = {"password": password}
        if username:
            credentials["username"] = username
        if phone_number:
            credentials["phone_number"] = phone_number

        user = authenticate(request=self.context.get("request"), **credentials)
        if not user:
            raise serializers.ValidationError("Unable to log in with provided credentials.")
        attrs["user"] = user
        return attrs
