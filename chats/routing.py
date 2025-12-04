from django.urls import path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    path("ws/session/<session_id>/", ChatConsumer.as_asgi()),
]
