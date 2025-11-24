from django.contrib import admin

from .models import User, UserSettings


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "phone_number", "is_online", "date_joined")
    search_fields = ("username", "email", "phone_number", "display_name")
    list_filter = ("is_online", "is_staff", "date_joined")
    readonly_fields = ("date_joined", "last_login")


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ("user", "theme", "language", "enable_notifications", "updated_at")
    list_filter = ("theme", "language", "enable_notifications")
    search_fields = ("user__username",)
