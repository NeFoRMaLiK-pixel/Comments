from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer

from .models import Comment, CommentEvent
from .services import invalidate_comment_cache


@shared_task
def process_comment_created_event(comment_id: int) -> None:
    comment = Comment.objects.select_related("parent").filter(id=comment_id).first()
    if not comment:
        return

    payload = {
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

    CommentEvent.objects.create(
        event_type="comment.created",
        comment=comment,
        payload=payload,
    )

    invalidate_comment_cache()

    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    async_to_sync(channel_layer.group_send)(
        "comments_feed",
        {
            "type": "comment_created",
            "payload": {
                "type": "comment.created",
                "comment": payload,
            },
        },
    )
