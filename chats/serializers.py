from rest_framework import serializers
from .models import ChatSession, Message


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    class Meta:
        model = Message
        fields = ['id', 'text', 'timestamp', 'sender', 'sender_username']
    
class ChatSessionSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = ['session_id', 'customer', 'supporter', 'status', 'created_at', 'messages']
