# chats/consumers.py
import json
import random
import string
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chats.models import User, ChatSession, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # session_id comes from URL path: /ws/session/<session_id>/
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.group_name = f"session_{self.session_id}"

        # Join the session group (same group for agent+visitor)
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        # Determine user: prefer authenticated user when available
        if self.scope.get("user") and self.scope["user"].is_authenticated:
            self.user = self.scope["user"]
        else:
            # Not authenticated -> decide role from query string (for dev/testing)
            # We look into the raw query string bytes in self.scope['query_string']
            # Example client will connect to: ws://.../ws/session/<id>/?role=agent
            qs = self.scope.get("query_string", b"").decode()
            role_hint = None
            if "role=agent" in qs or "role=supporter" in qs:
                role_hint = "supporter"
            elif "role=visitor" in qs or "role=customer" in qs:
                role_hint = "customer"
            self.user = await self.get_or_create_user_by_role(role_hint)

        await self.accept()

        # Immediately send init info (so client knows "who I am")
        await self.send(text_data=json.dumps({
            "type": "init",
            "username": self.user.username,
            "role": self.user.role,
        }))

        print(f"[CONNECT] {self.user.username} ({self.user.role}) connected to session {self.session_id}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    @database_sync_to_async
    def get_or_create_user_by_role(self, role_hint=None):
        """
        Create a temporary user for testing when not authenticated.
        If role_hint == "supporter" the created user will be an agent.
        Otherwise it will be a customer/visitor.
        """
        if role_hint == "supporter":
            username = "agent_" + "".join(random.choices(string.ascii_letters + string.digits, k=6))
            role = "supporter"
        else:
            username = "visitor_" + "".join(random.choices(string.ascii_letters + string.digits, k=6))
            role = "customer"

        # Create a simple user record (no password needed for these test users)
        user = User.objects.create(username=username, role=role)
        return user

    async def receive(self, text_data):
        """
        Incoming message from WebSocket client.
        Save the message and broadcast to the session group.
        """
        try:
            data = json.loads(text_data)
        except Exception:
            return

        msg = data.get("message")
        if not msg:
            return

        # Persist message
        await self.save_message(msg)

        # Broadcast to all members of the session group
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat_message",
                "message": msg,
                "username": self.user.username,
                "role": self.user.role
            }
        )

    async def chat_message(self, event):
        # Sent to WebSocket client
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, text):
        # Ensure a ChatSession object exists for this session_id
        # If it does not exist, create it and (best-effort) set customer/supporter
        session, created = ChatSession.objects.get_or_create(
            session_id=self.session_id,
            defaults={
                "customer": self.user if self.user.role == "customer" else None,
                "supporter": self.user if self.user.role == "supporter" else None,
                "status": "active"
            }
        )

        # If the session exists and the connecting user is supporter and supporter is empty, set it
        if not created and self.user.role == "supporter" and session.supporter is None:
            session.supporter = self.user
            session.save()

        # If the session exists and the connecting user is customer and customer is empty, set it
        if not created and self.user.role == "customer" and session.customer is None:
            session.customer = self.user
            session.save()

        # Save the message
        Message.objects.create(session=session, sender=self.user, text=text)
