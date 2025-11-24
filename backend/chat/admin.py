from django.contrib import admin

from .models import (
    Attachment, Conversation, ConversationMembership, Message, MessageReceipt,
    MessageReaction, Contact, PinnedMessage,
    Call, CallParticipant, Notification
)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "conversation_type", "owner", "is_public", "created_at")
    list_filter = ("conversation_type", "is_public", "created_at")
    search_fields = ("title", "owner__username")


@admin.register(ConversationMembership)
class ConversationMembershipAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "user", "is_admin", "joined_at")
    list_filter = ("is_admin", "joined_at")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "sender", "message_type", "created_at", "is_deleted")
    list_filter = ("message_type", "is_deleted", "created_at")
    search_fields = ("content", "sender__username")


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "file_name", "file_size", "mime_type")


admin.site.register(MessageReceipt)
admin.site.register(MessageReaction)
admin.site.register(Contact)
admin.site.register(PinnedMessage)


@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    list_display = ("id", "caller", "call_type", "state", "started_at", "duration")
    list_filter = ("call_type", "state", "started_at")


admin.site.register(CallParticipant)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "notification_type", "title", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("user__username", "title")
