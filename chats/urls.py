from django.urls import path
from . import views_api

urlpatterns = [
    path("users/", views_api.get_users),
    path("session/start/", views_api.start_session),
    path("session/<str:session_id>/", views_api.get_session),
    path("session/<str:session_id>/messages/", views_api.get_messages),
]
