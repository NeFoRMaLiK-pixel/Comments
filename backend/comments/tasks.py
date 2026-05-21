import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

try:
    from celery import shared_task
except ImportError:
    def shared_task(*decorator_args, **decorator_kwargs):
        # Local fallback when Celery is not installed: keep the same call shape.
        def decorator(func):
            func.delay = func
            return func

        if decorator_args and callable(decorator_args[0]) and len(decorator_args) == 1 and not decorator_kwargs:
            return decorator(decorator_args[0])

        return decorator

from .models import Comment, CommentEvent
from .services import invalidate_comment_cache

logger = logging.getLogger(__name__)
COMMENTS_GROUP_NAME = "comments_feed"


def build_comment_payload(comment: Comment) -> dict:
    return {
        "id": comment.id,
        "parent": comment.parent_id,
        "username": comment.username,
        "email": comment.email,
        "homepage": comment.homepage,
        "text_html": comment.text_html,
        "attachment_type": comment.attachment_type,
        "attachment_name": comment.attachment_name,
        "attachment_url": comment.attachment.url if comment.attachment else "",
        "created_at": comment.created_at.isoformat(),
    }


def send_comment_created_event(payload: dict) -> None:
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    try:
        async_to_sync(channel_layer.group_send)(
            COMMENTS_GROUP_NAME,
            {
                "type": "comment_created",
                "payload": {
                    "type": "comment_created",
                    "comment": payload,
                },
            },
        )
    except Exception:
        logger.exception("Failed to broadcast comment.created event.")


def broadcast_comment_created(comment_id: int) -> None:
    comment = Comment.objects.select_related("parent").filter(id=comment_id).first()
    if not comment:
        return

    payload = build_comment_payload(comment)
    send_comment_created_event(payload)


@shared_task(ignore_result=True)
def process_comment_created_event(comment_id: int) -> None:
    comment = Comment.objects.select_related("parent").filter(id=comment_id).first()
    if not comment:
        return

    payload = build_comment_payload(comment)

    try:
        CommentEvent.objects.create(
            event_type="comment.created",
            comment=comment,
            payload=payload,
        )
    except Exception:
        logger.exception("Failed to persist comment event for comment_id=%s", comment_id)

    invalidate_comment_cache()
