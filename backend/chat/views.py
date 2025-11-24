from django.db import models
from django.db.models import Q, Count
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import exceptions, mixins, permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import (
    Conversation, ConversationMembership, Message, 
    MessageReaction, Contact, PinnedMessage, Attachment,
    Call, CallParticipant
)
from .serializers import (
    ConversationSerializer, MessageSerializer, 
    MessageReactionSerializer, ContactSerializer, PinnedMessageSerializer,
    CallSerializer
)

User = get_user_model()


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(memberships__user=user).distinct()

    def perform_create(self, serializer):
        conversation = serializer.save(owner=self.request.user)
        # Add creator as admin
        ConversationMembership.objects.create(conversation=conversation, user=self.request.user, is_admin=True)
        
        # Add other members from request
        member_ids = self.request.data.get("member_ids", [])
        for user_id in member_ids:
            try:
                ConversationMembership.objects.get_or_create(
                    conversation=conversation,
                    user_id=int(user_id),
                    defaults={'is_admin': False}
                )
            except Exception as e:
                print(f"Failed to add member {user_id}: {e}")

    @action(detail=False, methods=["post"], url_path="create-direct")
    def create_direct(self, request):
        """Create a direct chat between two users"""
        try:
            other_user_id = request.data.get("user_id")
            
            print(f"[create_direct] Request from: {request.user.username}")
            print(f"[create_direct] Target user_id: {other_user_id}")
            
            if not other_user_id:
                return Response({"error": "user_id required."}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                other_user = User.objects.get(id=other_user_id)
                print(f"[create_direct] Found user: {other_user.username}")
            except User.DoesNotExist:
                print(f"[create_direct] User not found: {other_user_id}")
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
            
            # Check for existing direct conversation
            existing = Conversation.objects.filter(
                conversation_type=Conversation.DIRECT,
                memberships__user=request.user
            ).filter(
                memberships__user=other_user
            ).annotate(
                member_count=Count('memberships')
            ).filter(member_count=2).first()
            
            if existing:
                print(f"[create_direct] Found existing conversation: {existing.id}")
                serializer = self.get_serializer(existing)
                return Response(serializer.data)
            
            # Create new conversation
            print(f"[create_direct] Creating new conversation")
            conversation = Conversation.objects.create(
                title=f"{request.user.username} - {other_user.username}",
                conversation_type=Conversation.DIRECT,
                owner=request.user
            )
            
            # Add both users
            ConversationMembership.objects.create(
                conversation=conversation,
                user=request.user,
                is_admin=True
            )
            ConversationMembership.objects.create(
                conversation=conversation,
                user=other_user,
                is_admin=False
            )
            
            print(f"[create_direct] Conversation created: {conversation.id}")
            serializer = self.get_serializer(conversation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"[create_direct] ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {"error": f"Failed to create conversation: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"], url_path="add-member")
    def add_member(self, request, pk=None):
        conversation = self.get_object()
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"detail": "user_id required."}, status=400)
        ConversationMembership.objects.get_or_create(conversation=conversation, user_id=user_id)
        return Response({"status": "member added"})


class MessageViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        conversation_id = self.kwargs.get("conversation_pk")
        qs = Message.objects.filter(conversation_id=conversation_id, conversation__memberships__user=user)
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(Q(content__icontains=search))
        return qs.select_related("sender", "conversation").prefetch_related("attachments", "receipts")

    def perform_create(self, serializer):
        conversation = Conversation.objects.filter(
            id=self.kwargs.get("conversation_pk"), memberships__user=self.request.user
        ).first()
        if not conversation:
            raise exceptions.PermissionDenied("You are not a member of this conversation.")
        serializer.save(sender=self.request.user, conversation=conversation)

    def perform_update(self, serializer):
        message = self.get_object()
        if message.sender != self.request.user:
            raise exceptions.PermissionDenied("You can only edit your own messages.")
        serializer.save(edited_at=timezone.now())

    def perform_destroy(self, instance):
        if instance.sender != self.request.user:
            raise exceptions.PermissionDenied("You can only delete your own messages.")
        instance.is_deleted = True
        instance.save()

    @action(detail=True, methods=["patch"], url_path="edit")
    def edit_message(self, request, pk=None, conversation_pk=None):
        """Edit a message"""
        message = self.get_object()
        if message.sender != request.user:
            return Response({"detail": "You can only edit your own messages."}, status=status.HTTP_403_FORBIDDEN)
        
        new_content = request.data.get("content")
        if not new_content:
            return Response({"detail": "content required."}, status=status.HTTP_400_BAD_REQUEST)
        
        message.content = new_content
        message.edited_at = timezone.now()
        message.save()
        
        # Send WebSocket notification
        channel_layer = get_channel_layer()
        group_name = f"conversation_{conversation_pk}"
        serializer = self.get_serializer(message)
        
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "message.edited",
                "message": serializer.data,
            }
        )
        
        return Response(serializer.data)

    @action(detail=True, methods=["delete"], url_path="soft-delete")
    def soft_delete_message(self, request, pk=None, conversation_pk=None):
        """Soft delete a message"""
        message = self.get_object()
        if message.sender != request.user:
            return Response({"detail": "You can only delete your own messages."}, status=status.HTTP_403_FORBIDDEN)
        
        message.is_deleted = True
        message.save()
        
        # Send WebSocket notification
        channel_layer = get_channel_layer()
        group_name = f"conversation_{conversation_pk}"
        
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "message.deleted",
                "message_id": message.id,
            }
        )
        
        return Response({"status": "message deleted"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="react")
    def react(self, request, pk=None, conversation_pk=None):
        """Add or remove a reaction to a message"""
        message = self.get_object()
        emoji = request.data.get("emoji")
        
        if not emoji:
            return Response({"detail": "emoji required."}, status=status.HTTP_400_BAD_REQUEST)
        
        reaction, created = MessageReaction.objects.get_or_create(
            message=message,
            user=request.user,
            emoji=emoji
        )
        
        if not created:
            reaction.delete()
            return Response({"status": "reaction removed"})
        
        serializer = MessageReactionSerializer(reaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="pin")
    def pin(self, request, pk=None, conversation_pk=None):
        """Pin a message in the conversation"""
        message = self.get_object()
        conversation = message.conversation
        
        membership = ConversationMembership.objects.filter(
            conversation=conversation,
            user=request.user,
            is_admin=True
        ).first()
        
        if not membership:
            return Response({"detail": "Only admins can pin messages."}, status=status.HTTP_403_FORBIDDEN)
        
        pinned, created = PinnedMessage.objects.get_or_create(
            conversation=conversation,
            message=message,
            defaults={'pinned_by': request.user}
        )
        
        serializer = PinnedMessageSerializer(pinned)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="forward")
    def forward(self, request, pk=None, conversation_pk=None):
        """Forward a message to another conversation"""
        message = self.get_object()
        target_conversation_id = request.data.get("conversation_id")
        
        if not target_conversation_id:
            return Response({"detail": "conversation_id required."}, status=status.HTTP_400_BAD_REQUEST)
        
        target_conversation = Conversation.objects.filter(
            id=target_conversation_id,
            memberships__user=request.user
        ).first()
        
        if not target_conversation:
            return Response({"detail": "Conversation not found."}, status=status.HTTP_404_NOT_FOUND)
        
        forwarded = Message.objects.create(
            conversation=target_conversation,
            sender=request.user,
            message_type=message.message_type,
            content=message.content,
            forwarded_from=message
        )
        
        serializer = MessageSerializer(forwarded)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Contact.objects.filter(owner=self.request.user).select_related('contact')

    def perform_create(self, serializer):
        contact_id = self.request.data.get("contact_id")
        if not contact_id:
            raise exceptions.ValidationError("contact_id required.")
        
        try:
            contact_user = User.objects.get(id=contact_id)
        except User.DoesNotExist:
            raise exceptions.ValidationError("User not found.")
        
        serializer.save(owner=self.request.user, contact=contact_user)

    @action(detail=True, methods=["post"], url_path="block")
    def block(self, request, pk=None):
        """Block/unblock a contact"""
        contact = self.get_object()
        contact.is_blocked = not contact.is_blocked
        contact.save()
        return Response({"status": "blocked" if contact.is_blocked else "unblocked"})

    @action(detail=True, methods=["post"], url_path="favorite")
    def favorite(self, request, pk=None):
        """Mark/unmark as favorite"""
        contact = self.get_object()
        contact.is_favorite = not contact.is_favorite
        contact.save()
        return Response({"status": "favorited" if contact.is_favorite else "unfavorited"})


class UserSearchViewSet(viewsets.ReadOnlyModelViewSet):
    """Search for users to add to contacts or conversations"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        query = self.request.query_params.get("q", "")
        if len(query) < 2:
            return User.objects.none()
        
        queryset = User.objects.filter(
            Q(username__icontains=query) |
            Q(display_name__icontains=query) |
            Q(phone_number__icontains=query)
        ).exclude(id=self.request.user.id)[:20]
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """List users matching search query"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def get_serializer_class(self):
        from accounts.serializers import UserSerializer
        return UserSerializer


from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from .models import Attachment


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_attachment(request, attachment_id):
    """Download attachment file with proper permissions check"""
    try:
        attachment = get_object_or_404(Attachment, id=attachment_id)
        
        # Check if user has access to this conversation
        conversation = attachment.message.conversation
        if not conversation.memberships.filter(user=request.user).exists():
            raise exceptions.PermissionDenied("You don't have access to this file")
        
        # Get the file
        if not attachment.file:
            raise Http404("File not found")
        
        # Check if using S3 storage (for production)
        from django.conf import settings
        use_s3 = getattr(settings, 'USE_S3', False)
        
        if use_s3:
            # For S3, redirect to the signed URL  
            from django.shortcuts import redirect
            file_url = attachment.file.url
            return redirect(file_url)
        else:
            # For local development, serve the file directly
            from django.http import FileResponse
            import os
            
            # Check if file exists
            try:
                file_path = attachment.file.path
                if not os.path.exists(file_path):
                    raise Http404("File not found on disk")
                
                response = FileResponse(
                    open(file_path, 'rb'),
                    content_type=attachment.mime_type or 'application/octet-stream'
                )
                response['Content-Disposition'] = f'attachment; filename="{attachment.file_name}"'
                response['Access-Control-Allow-Origin'] = '*'  # Allow CORS for file downloads
                response['Access-Control-Allow-Methods'] = 'GET'
                response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
                
                return response
            except ValueError:
                # If file.path fails (e.g., with S3 URLs), try to serve via URL
                from django.shortcuts import redirect
                return redirect(attachment.file.url)
        
    except Exception as e:
        raise Http404(f"File not found: {str(e)}")


class CallViewSet(viewsets.ModelViewSet):
    serializer_class = CallSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Get calls from conversations the user is a member of
        return Call.objects.filter(
            conversation__memberships__user=user
        ).select_related('caller', 'conversation').prefetch_related('participants__user').distinct()

    def perform_create(self, serializer):
        # Get conversation and validate membership
        conversation_id = self.request.data.get('conversation_id')
        conversation = get_object_or_404(Conversation, id=conversation_id)
        
        # Check if user is a member of the conversation
        if not conversation.memberships.filter(user=self.request.user).exists():
            raise exceptions.PermissionDenied("You are not a member of this conversation")
        
        call = serializer.save(caller=self.request.user, conversation=conversation)
        
        # Add caller as a participant
        CallParticipant.objects.create(
            call=call,
            user=self.request.user,
            is_answered=True
        )

    @action(detail=True, methods=['post'])
    def answer(self, request, pk=None):
        """Answer a call"""
        call = self.get_object()
        
        # Check if user is a participant
        participant, created = CallParticipant.objects.get_or_create(
            call=call,
            user=request.user,
            defaults={'is_answered': True}
        )
        
        if not created:
            participant.is_answered = True
            participant.save()
        
        call.state = Call.ACTIVE
        call.save()
        
        return Response({'status': 'answered'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a call"""
        call = self.get_object()
        call.state = Call.DECLINED
        call.save()
        
        return Response({'status': 'rejected'})

    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """End a call"""
        call = self.get_object()
        call.state = Call.ENDED
        call.ended_at = timezone.now()
        
        # Calculate duration if call was active
        if call.started_at:
            duration = (call.ended_at - call.started_at).total_seconds()
            call.duration = int(duration)
        
        call.save()
        
        return Response({'status': 'ended', 'duration': call.duration})

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active calls for the user"""
        user = request.user
        active_calls = self.get_queryset().filter(
            state__in=[Call.INITIATED, Call.RINGING, Call.ACTIVE],
            participants__user=user
        )
        serializer = self.get_serializer(active_calls, many=True)
        return Response(serializer.data)
