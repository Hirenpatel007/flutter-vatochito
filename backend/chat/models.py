from django.conf import settings
from django.db import models
from django.utils import timezone

from core.utils import generate_upload_path


class Conversation(models.Model):
    DIRECT = "direct"
    GROUP = "group"
    CHANNEL = "channel"
    CONVERSATION_TYPES = [
        (DIRECT, "Direct"),
        (GROUP, "Group"),
        (CHANNEL, "Channel"),
    ]

    title = models.CharField(max_length=255, blank=True)
    conversation_type = models.CharField(max_length=16, choices=CONVERSATION_TYPES, default=DIRECT)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owned_conversations", on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    avatar = models.ImageField(upload_to=generate_upload_path, null=True, blank=True)
    is_public = models.BooleanField(default=False)
    invite_link = models.CharField(max_length=255, blank=True, unique=True, null=True)

    def __str__(self) -> str:
        return self.title or f"Conversation {self.pk}"


class ConversationMembership(models.Model):
    conversation = models.ForeignKey(Conversation, related_name="memberships", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="memberships", on_delete=models.CASCADE)
    nickname = models.CharField(max_length=255, blank=True)
    is_admin = models.BooleanField(default=False)
    joined_at = models.DateTimeField(default=timezone.now)
    muted_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("conversation", "user")


class Message(models.Model):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    MESSAGE_TYPES = [
        (TEXT, "Text"),
        (IMAGE, "Image"),
        (VIDEO, "Video"),
        (AUDIO, "Audio"),
        (FILE, "File"),
    ]

    conversation = models.ForeignKey(Conversation, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="messages", on_delete=models.CASCADE)
    message_type = models.CharField(max_length=16, choices=MESSAGE_TYPES, default=TEXT)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    edited_at = models.DateTimeField(null=True, blank=True)
    reply_to = models.ForeignKey("self", null=True, blank=True, related_name="replies", on_delete=models.SET_NULL)
    forwarded_from = models.ForeignKey("self", null=True, blank=True, related_name="forwards", on_delete=models.SET_NULL)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]


class Attachment(models.Model):
    message = models.ForeignKey(Message, related_name="attachments", on_delete=models.CASCADE)
    file = models.FileField(upload_to=generate_upload_path)
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(default=0)
    mime_type = models.CharField(max_length=128, blank=True)


class MessageReceipt(models.Model):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    RECEIPT_STATES = [
        (SENT, "Sent"),
        (DELIVERED, "Delivered"),
        (READ, "Read"),
    ]

    message = models.ForeignKey(Message, related_name="receipts", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="receipts", on_delete=models.CASCADE)
    state = models.CharField(max_length=16, choices=RECEIPT_STATES, default=SENT)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("message", "user")


class MessageReaction(models.Model):
    message = models.ForeignKey(Message, related_name="reactions", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="reactions", on_delete=models.CASCADE)
    emoji = models.CharField(max_length=10)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("message", "user", "emoji")


class Contact(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="contacts", on_delete=models.CASCADE)
    contact = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="contact_of", on_delete=models.CASCADE)
    nickname = models.CharField(max_length=255, blank=True)
    is_blocked = models.BooleanField(default=False)
    is_favorite = models.BooleanField(default=False)
    added_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("owner", "contact")


class PinnedMessage(models.Model):
    conversation = models.ForeignKey(Conversation, related_name="pinned_messages", on_delete=models.CASCADE)
    message = models.ForeignKey(Message, related_name="pinned_in", on_delete=models.CASCADE)
    pinned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pinned_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("conversation", "message")


class Call(models.Model):
    VOICE = "voice"
    VIDEO = "video"
    CALL_TYPES = [
        (VOICE, "Voice"),
        (VIDEO, "Video"),
    ]
    
    INITIATED = "initiated"
    RINGING = "ringing"
    ACTIVE = "active"
    ENDED = "ended"
    MISSED = "missed"
    DECLINED = "declined"
    CALL_STATES = [
        (INITIATED, "Initiated"),
        (RINGING, "Ringing"),
        (ACTIVE, "Active"),
        (ENDED, "Ended"),
        (MISSED, "Missed"),
        (DECLINED, "Declined"),
    ]
    
    conversation = models.ForeignKey(Conversation, related_name="calls", on_delete=models.CASCADE)
    caller = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="calls_made", on_delete=models.CASCADE)
    call_type = models.CharField(max_length=16, choices=CALL_TYPES, default=VOICE)
    state = models.CharField(max_length=16, choices=CALL_STATES, default=INITIATED)
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration = models.PositiveIntegerField(default=0, help_text="Duration in seconds")
    
    def __str__(self):
        return f"{self.get_call_type_display()} call by {self.caller.username}"


class CallParticipant(models.Model):
    call = models.ForeignKey(Call, related_name="participants", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="call_participations", on_delete=models.CASCADE)
    joined_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)
    is_answered = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ("call", "user")


class Notification(models.Model):
    MESSAGE = "message"
    MENTION = "mention"
    CALL = "call"
    GROUP_INVITE = "group_invite"
    CONTACT_REQUEST = "contact_request"
    
    NOTIFICATION_TYPES = [
        (MESSAGE, "New Message"),
        (MENTION, "Mention"),
        (CALL, "Call"),
        (GROUP_INVITE, "Group Invite"),
        (CONTACT_REQUEST, "Contact Request"),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="notifications", on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=32, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    # Optional references
    related_conversation = models.ForeignKey(Conversation, null=True, blank=True, on_delete=models.CASCADE)
    related_message = models.ForeignKey(Message, null=True, blank=True, on_delete=models.CASCADE)
    related_call = models.ForeignKey(Call, null=True, blank=True, on_delete=models.CASCADE)
    related_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name="notifications_from", on_delete=models.CASCADE)
    
    class Meta:
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.get_notification_type_display()} for {self.user.username}"
