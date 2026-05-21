from django.urls import re_path

from .consumers import CommentFeedConsumer

websocket_urlpatterns = [
    re_path(r"ws/comments/$", CommentFeedConsumer.as_asgi()),
]
