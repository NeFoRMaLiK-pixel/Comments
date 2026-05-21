from django.urls import path

from .views import CaptchaView, CommentListCreateView, CommentPreviewView

urlpatterns = [
    path("", CommentListCreateView.as_view(), name="comment-list-create"),
    path("captcha/", CaptchaView.as_view(), name="captcha"),
    path("preview/", CommentPreviewView.as_view(), name="comment-preview"),
]
