from uuid import uuid4
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import ChatSession, Message, User
from django.contrib.auth.decorators import login_required

def index(request):
    users = User.objects.exclude(username=request.user.username)
    context = {
        'users' : users
    }
    return render(request, 'index.html', context)

def start_chat(request):
    
    if request.user.role != "customer":
        return HttpResponse("Only customers can start chat sessions.")

    # Auto-assign supporter
    supporter = User.objects.filter(role="supporter").order_by('id').first()
    if not supporter:
        return HttpResponse("No support agents available.")

    # Create session
    session_id = uuid4().hex
    session = ChatSession.objects.create(
        session_id=session_id,
        customer=request.user,
        supporter=supporter,
        status="active"
    )

    return redirect("chat_page", session_id=session_id)


def chat_page(request, session_id):
    try:
        session = ChatSession.objects.get(session_id=session_id)
    except ChatSession.DoesNotExist:
        return HttpResponse("Chat session not found")

    messages = Message.objects.filter(session=session)

    return render(request, "chat.html", {
        "session": session,
        "messages": messages
    })
