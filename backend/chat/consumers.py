import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Conversation, Message, Call, CallParticipant
from .serializers import MessageSerializer

User = get_user_model()


class ConversationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        try:
            self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
            self.group_name = f"conversation_{self.conversation_id}"
            
            print(f"[WebSocket] User attempting to connect: {self.scope['user']}")
            
            if self.scope["user"].is_anonymous:
                print(f"[WebSocket] Anonymous user, closing connection")
                await self.close()
                return
                
            is_member = await self._is_member()
            if not is_member:
                print(f"[WebSocket] User {self.scope['user']} is not a member of conversation {self.conversation_id}")
                await self.close()
                return
                
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            print(f"[WebSocket] Connection accepted for user {self.scope['user']} in conversation {self.conversation_id}")
            
        except Exception as e:
            print(f"[WebSocket] Error during connect: {e}")
            await self.close()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        event_type = content.get("type")
        
        # Handle ping/pong for keeping connection alive
        if event_type == "ping":
            await self.send_json({"type": "pong"})
            return
        
        if event_type == "message.send":
            message = await self._create_message(content)
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "message.broadcast",
                    "message": message,
                },
            )
        elif event_type == "typing":
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "typing.indicator",
                    "user_id": self.scope["user"].id,
                    "username": self.scope["user"].username,
                    "is_typing": content.get("is_typing", True),
                },
            )
        elif event_type == "message.read":
            message_id = content.get("message_id")
            await self._mark_as_read(message_id)
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "message.read_receipt",
                    "message_id": message_id,
                    "user_id": self.scope["user"].id,
                },
            )
        elif event_type == "message.edit":
            message_id = content.get("message_id")
            new_content = content.get("content")
            edited_message = await self._edit_message(message_id, new_content)
            if edited_message:
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "message.edited",
                        "message": edited_message,
                    },
                )
        elif event_type == "message.delete":
            message_id = content.get("message_id")
            deleted_message = await self._delete_message(message_id)
            if deleted_message:
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "message.deleted",
                        "message_id": message_id,
                    },
                )
        
        # WebRTC Call signaling
        elif event_type == "call.initiate":
            await self._handle_call_initiate(content)
        elif event_type == "call.answer":
            await self._handle_call_answer(content)
        elif event_type == "call.reject":
            await self._handle_call_reject(content)
        elif event_type == "call.end":
            await self._handle_call_end(content)
        elif event_type == "webrtc.offer":
            await self._handle_webrtc_offer(content)
        elif event_type == "webrtc.answer":
            await self._handle_webrtc_answer(content)
        elif event_type == "webrtc.ice_candidate":
            await self._handle_ice_candidate(content)

    async def message_broadcast(self, event):
        await self.send_json({"type": "message.new", "data": event["message"]})

    async def typing_indicator(self, event):
        # Don't send typing indicator back to the sender
        if event["user_id"] != self.scope["user"].id:
            await self.send_json({
                "type": "typing",
                "user_id": event["user_id"],
                "username": event["username"],
                "is_typing": event["is_typing"],
            })

    async def message_read_receipt(self, event):
        await self.send_json({
            "type": "message.read",
            "message_id": event["message_id"],
            "user_id": event["user_id"],
        })

    async def message_edited(self, event):
        await self.send_json({
            "type": "message.edited",
            "data": event["message"],
        })

    async def message_deleted(self, event):
        await self.send_json({
            "type": "message.deleted",
            "message_id": event["message_id"],
        })

    # WebRTC signaling broadcast methods
    async def call_incoming(self, event):
        await self.send_json({
            "type": "call.incoming",
            "call_id": event["call_id"],
            "caller": event["caller"],
            "call_type": event["call_type"],
        })

    async def call_answered(self, event):
        await self.send_json({
            "type": "call.answered",
            "call_id": event["call_id"],
            "answerer": event["answerer"],
        })

    async def call_rejected(self, event):
        await self.send_json({
            "type": "call.rejected",
            "call_id": event["call_id"],
            "rejector": event["rejector"],
        })

    async def call_ended(self, event):
        await self.send_json({
            "type": "call.ended",
            "call_id": event["call_id"],
            "ended_by": event["ended_by"],
        })

    async def webrtc_offer(self, event):
        # Don't send offer back to sender
        if event["sender_id"] != self.scope["user"].id:
            await self.send_json({
                "type": "webrtc.offer",
                "call_id": event["call_id"],
                "offer": event["offer"],
                "sender_id": event["sender_id"],
            })

    async def webrtc_answer(self, event):
        # Don't send answer back to sender
        if event["sender_id"] != self.scope["user"].id:
            await self.send_json({
                "type": "webrtc.answer",
                "call_id": event["call_id"],
                "answer": event["answer"],
                "sender_id": event["sender_id"],
            })

    async def webrtc_ice_candidate(self, event):
        # Don't send ice candidate back to sender
        if event["sender_id"] != self.scope["user"].id:
            await self.send_json({
                "type": "webrtc.ice_candidate",
                "call_id": event["call_id"],
                "candidate": event["candidate"],
                "sender_id": event["sender_id"],
            })

    @database_sync_to_async
    def _is_member(self):
        try:
            return Conversation.objects.filter(
                id=self.conversation_id, 
                memberships__user=self.scope["user"]
            ).exists()
        except Exception as e:
            print(f"[WebSocket] Error checking membership: {e}")
            return False

    @database_sync_to_async
    def _create_message(self, payload):
        try:
            message = Message.objects.create(
                conversation_id=self.conversation_id,
                sender=self.scope["user"],
                content=payload.get("content", ""),
                message_type=payload.get("message_type", "text"),
            )
            return MessageSerializer(message).data
        except Exception as e:
            print(f"[WebSocket] Error creating message: {e}")
            return None

    @database_sync_to_async
    def _mark_as_read(self, message_id):
        from .models import MessageReceipt
        if message_id:
            MessageReceipt.objects.update_or_create(
                message_id=message_id,
                user=self.scope["user"],
                defaults={"state": "read"}
            )

    @database_sync_to_async
    def _edit_message(self, message_id, new_content):
        try:
            message = Message.objects.get(
                id=message_id,
                conversation_id=self.conversation_id,
                sender=self.scope["user"]
            )
            if new_content:
                message.content = new_content
                message.edited_at = timezone.now()
                message.save()
                return MessageSerializer(message).data
        except Message.DoesNotExist:
            print(f"[WebSocket] Message {message_id} not found or not owned by user")
        except Exception as e:
            print(f"[WebSocket] Error editing message: {e}")
        return None

    @database_sync_to_async
    def _delete_message(self, message_id):
        try:
            message = Message.objects.get(
                id=message_id,
                conversation_id=self.conversation_id,
                sender=self.scope["user"]
            )
            message.is_deleted = True
            message.save()
            return True
        except Message.DoesNotExist:
            print(f"[WebSocket] Message {message_id} not found or not owned by user")
        except Exception as e:
            print(f"[WebSocket] Error deleting message: {e}")
        return False

    # WebRTC Call handling methods
    @database_sync_to_async
    def _create_call(self, call_type, participant_ids):
        try:
            call = Call.objects.create(
                conversation_id=self.conversation_id,
                caller=self.scope["user"],
                call_type=call_type,
                state=Call.INITIATED
            )
            
            # Add caller as participant
            CallParticipant.objects.create(
                call=call,
                user=self.scope["user"],
                is_answered=True,
                joined_at=timezone.now()
            )
            
            # Add other participants
            for user_id in participant_ids:
                if user_id != self.scope["user"].id:
                    CallParticipant.objects.create(
                        call=call,
                        user_id=user_id
                    )
            
            return call.id
        except Exception as e:
            print(f"[WebSocket] Error creating call: {e}")
            return None

    @database_sync_to_async
    def _update_call_state(self, call_id, state, user_action=None):
        try:
            call = Call.objects.get(id=call_id)
            call.state = state
            if state == Call.ENDED:
                call.ended_at = timezone.now()
                # Calculate duration
                if call.started_at:
                    duration = (call.ended_at - call.started_at).total_seconds()
                    call.duration = int(duration)
            call.save()
            
            if user_action == 'answer':
                participant = CallParticipant.objects.get(call=call, user=self.scope["user"])
                participant.is_answered = True
                participant.joined_at = timezone.now()
                participant.save()
                
                # Update call state to active when answered
                call.state = Call.ACTIVE
                call.save()
            
            return True
        except Exception as e:
            print(f"[WebSocket] Error updating call state: {e}")
            return False

    async def _handle_call_initiate(self, content):
        call_type = content.get("call_type", "voice")  # voice or video
        participant_ids = content.get("participant_ids", [])
        
        call_id = await self._create_call(call_type, participant_ids)
        if call_id:
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "call.incoming",
                    "call_id": call_id,
                    "caller": {
                        "id": self.scope["user"].id,
                        "username": self.scope["user"].username,
                        "first_name": self.scope["user"].first_name,
                        "last_name": self.scope["user"].last_name,
                    },
                    "call_type": call_type,
                }
            )

    async def _handle_call_answer(self, content):
        call_id = content.get("call_id")
        if call_id:
            success = await self._update_call_state(call_id, Call.ACTIVE, 'answer')
            if success:
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "call.answered",
                        "call_id": call_id,
                        "answerer": {
                            "id": self.scope["user"].id,
                            "username": self.scope["user"].username,
                        }
                    }
                )

    async def _handle_call_reject(self, content):
        call_id = content.get("call_id")
        if call_id:
            success = await self._update_call_state(call_id, Call.DECLINED)
            if success:
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "call.rejected",
                        "call_id": call_id,
                        "rejector": {
                            "id": self.scope["user"].id,
                            "username": self.scope["user"].username,
                        }
                    }
                )

    async def _handle_call_end(self, content):
        call_id = content.get("call_id")
        if call_id:
            success = await self._update_call_state(call_id, Call.ENDED)
            if success:
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "call.ended",
                        "call_id": call_id,
                        "ended_by": {
                            "id": self.scope["user"].id,
                            "username": self.scope["user"].username,
                        }
                    }
                )

    async def _handle_webrtc_offer(self, content):
        call_id = content.get("call_id")
        offer = content.get("offer")
        
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "webrtc.offer",
                "call_id": call_id,
                "offer": offer,
                "sender_id": self.scope["user"].id,
            }
        )

    async def _handle_webrtc_answer(self, content):
        call_id = content.get("call_id")
        answer = content.get("answer")
        
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "webrtc.answer",
                "call_id": call_id,
                "answer": answer,
                "sender_id": self.scope["user"].id,
            }
        )

    async def _handle_ice_candidate(self, content):
        call_id = content.get("call_id")
        candidate = content.get("candidate")
        
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "webrtc.ice_candidate",
                "call_id": call_id,
                "candidate": candidate,
                "sender_id": self.scope["user"].id,
            }
        )
