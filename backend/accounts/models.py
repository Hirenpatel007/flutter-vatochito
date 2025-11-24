from django.contrib.auth.models import AbstractUser
from django.db import models

from core.utils import generate_upload_path


class User(AbstractUser):
    display_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=32, unique=True, null=True, blank=True)
    avatar = models.ImageField(upload_to=generate_upload_path, null=True, blank=True)
    status_message = models.CharField(max_length=255, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    is_online = models.BooleanField(default=False)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    
    # Profile fields
    date_of_birth = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    website = models.URLField(max_length=500, blank=True)
    
    # Privacy settings
    show_phone_number = models.BooleanField(default=False)
    show_last_seen = models.BooleanField(default=True)
    show_profile_photo = models.BooleanField(default=True)
    allow_calls = models.BooleanField(default=True)
    allow_group_invite = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.username or self.display_name or "User"


class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    
    # Notification settings
    enable_notifications = models.BooleanField(default=True)
    notification_sound = models.BooleanField(default=True)
    message_preview = models.BooleanField(default=True)
    
    # Chat settings
    enter_to_send = models.BooleanField(default=True)
    auto_download_photos = models.BooleanField(default=True)
    auto_download_videos = models.BooleanField(default=False)
    auto_download_files = models.BooleanField(default=False)
    
    # Security settings
    two_factor_enabled = models.BooleanField(default=False)
    show_typing_indicator = models.BooleanField(default=True)
    show_read_receipts = models.BooleanField(default=True)
    
    # Appearance
    theme = models.CharField(max_length=20, default='light', choices=[
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('auto', 'Auto')
    ])
    font_size = models.CharField(max_length=20, default='medium', choices=[
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large')
    ])
    
    # Language
    language = models.CharField(max_length=10, default='en', choices=[
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('ru', 'Russian'),
        ('ar', 'Arabic'),
        ('zh', 'Chinese')
    ])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Settings for {self.user.username}"
    
    class Meta:
        verbose_name_plural = "User Settings"
