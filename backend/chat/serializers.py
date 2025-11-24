from rest_framework import serializers

from .models import (
    Attachment, Conversation, ConversationMembership, Message, 
    MessageReceipt, MessageReaction, Contact, PinnedMessage,
    Call, CallParticipant
)
from accounts.serializers import UserSerializer


class AttachmentSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Attachment
        fields = ["id", "file", "file_name", "file_size", "mime_type", "download_url"]
        read_only_fields = ["id"]
    
    def get_download_url(self, obj):
        from django.urls import reverse
        return reverse('attachment-download', args=[obj.id])


class MessageReceiptSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = MessageReceipt
        fields = ["user", "state", "updated_at"]


class MessageReactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = MessageReaction
        fields = ["id", "user", "emoji", "created_at"]
        read_only_fields = ["id", "user", "created_at"]


class ContactSerializer(serializers.ModelSerializer):
    contact = UserSerializer(read_only=True)

    class Meta:
        model = Contact
        fields = ["id", "contact", "nickname", "is_blocked", "is_favorite", "added_at"]
        read_only_fields = ["id", "added_at"]


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    receipts = MessageReceiptSerializer(many=True, read_only=True)
    reactions = MessageReactionSerializer(many=True, read_only=True)
    reply_to_message = serializers.SerializerMethodField()
    forwarded_from_message = serializers.SerializerMethodField()
    
    # For file uploads (write-only)
    uploaded_files = serializers.ListField(
        child=serializers.FileField(max_length=100000, allow_empty_file=False),
        write_only=True,
        required=False
    )

    class Meta:
        model = Message
        fields = [
            "id",
            "conversation",
            "sender",
            "message_type",
            "content",
            "created_at",
            "edited_at",
            "reply_to",
            "reply_to_message",
            "forwarded_from",
            "forwarded_from_message",
            "is_deleted",
            "attachments",
            "receipts",
            "reactions",
            "uploaded_files",  # For file uploads
        ]
        read_only_fields = ["id", "sender", "created_at", "edited_at", "conversation"]

    def create(self, validated_data):
        uploaded_files = validated_data.pop('uploaded_files', [])
        message = super().create(validated_data)
        
        # Create attachments from uploaded files
        for file in uploaded_files:
            Attachment.objects.create(
                message=message,
                file=file,
                file_name=file.name,
                file_size=file.size,
                mime_type=file.content_type or 'application/octet-stream'
            )
        
        return message

    def get_reply_to_message(self, obj):
        if obj.reply_to:
            return {
                "id": obj.reply_to.id,
                "sender": UserSerializer(obj.reply_to.sender).data,
                "content": obj.reply_to.content[:100],
            }
        return None

    def get_forwarded_from_message(self, obj):
        if obj.forwarded_from:
            return {
                "id": obj.forwarded_from.id,
                "sender": UserSerializer(obj.forwarded_from.sender).data,
            }
        return None


class ConversationMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ConversationMembership
        fields = ["id", "user", "nickname", "is_admin", "joined_at", "muted_until"]
        read_only_fields = ["id", "joined_at"]


class PinnedMessageSerializer(serializers.ModelSerializer):
    message = MessageSerializer(read_only=True)
    pinned_by = UserSerializer(read_only=True)

    class Meta:
        model = PinnedMessage
        fields = ["id", "message", "pinned_by", "pinned_at"]
        read_only_fields = ["id", "pinned_by", "pinned_at"]


class ConversationSerializer(serializers.ModelSerializer):
    members = ConversationMembershipSerializer(source="memberships", many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "title",
            "conversation_type",
            "owner",
            "description",
            "created_at",
            "updated_at",
            "avatar",
            "is_public",
            "invite_link",
            "members",
            "last_message",
            "unread_count",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def get_last_message(self, obj):
        last_msg = obj.messages.filter(is_deleted=False).first()
        if last_msg:
            return MessageSerializer(last_msg).data
        return None

    def get_unread_count(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            return obj.messages.exclude(receipts__user=user, receipts__state='read').count()
        return 0


class CallParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = CallParticipant
        fields = ["id", "user", "joined_at", "left_at", "is_answered"]
        read_only_fields = ["id", "joined_at", "left_at"]


class CallSerializer(serializers.ModelSerializer):
    caller = UserSerializer(read_only=True)
    participants = CallParticipantSerializer(many=True, read_only=True)
    conversation = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Call
        fields = [
            "id", "conversation", "caller", "call_type", "state",
            "started_at", "ended_at", "duration", "participants"
        ]
        read_only_fields = ["id", "caller", "started_at", "ended_at", "duration"]
