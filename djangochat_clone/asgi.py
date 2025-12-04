# import os

# from django.core.asgi import get_asgi_application

# from django.urls import path

# from channels.routing import ProtocolTypeRouter, URLRouter

# from channels.auth import AuthMiddlewareStack

# from chats.consumers import PersonalChatConsumer

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangochat_clone.settings')

# application = get_asgi_application()

# application = ProtocolTypeRouter({
#     'websocket' : AuthMiddlewareStack(
#         URLRouter([
#             path('ws/<int:id>/', PersonalChatConsumer.as_asgi())
#         ])
#     )
# })



import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from chats.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangochat_clone.settings')

django_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})

