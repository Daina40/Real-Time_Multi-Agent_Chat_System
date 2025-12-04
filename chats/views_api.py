from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from chats.models import User, ChatSession, Message
from chats.serializers import ChatSessionSerializer, MessageSerializer
import uuid


# 1) List all users (customers + supporters)
@api_view(['GET'])
def get_users(request):
    users = User.objects.all()
    return Response([{"id": u.id, "username": u.username, "role": u.role} for u in users])


# 2) Create a new session
@api_view(['POST'])
def start_session(request):
    customer_id = request.data.get("customer_id")

    if not customer_id:
        return Response({"error": "customer_id required"}, status=400)

    session = ChatSession.objects.create(
        session_id=str(uuid.uuid4()),
        customer_id=customer_id,
        status="pending"
    )
    return Response({"session_id": session.session_id})


# 3) Get session details + messages
@api_view(['GET'])
def get_session(request, session_id):
    try:
        session = ChatSession.objects.get(session_id=session_id)
    except ChatSession.DoesNotExist:
        return Response({"error": "Session not found"}, status=404)

    serializer = ChatSessionSerializer(session)
    return Response(serializer.data)


# 4) Get message history
@api_view(['GET'])
def get_messages(request, session_id):
    try:
        session = ChatSession.objects.get(session_id=session_id)
    except ChatSession.DoesNotExist:
        return Response({"error": "Session not found"}, status=404)

    messages = session.messages.all()
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)
