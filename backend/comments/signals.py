import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Comment

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Comment)
def on_comment_created(sender, instance: Comment, created: bool, **kwargs):
    if not created:
        return

    comment_id = instance.id

    from .tasks import broadcast_comment_created, process_comment_created_event

    def handle_comment_created() -> None:
        # Immediate websocket broadcast from web process for realtime UX.
        broadcast_comment_created(comment_id)

        try:
            process_comment_created_event.delay(comment_id)
        except Exception:
            logger.exception("Failed to enqueue comment.created task. Falling back to sync processing.")
            process_comment_created_event(comment_id)

    transaction.on_commit(handle_comment_created, robust=True)
