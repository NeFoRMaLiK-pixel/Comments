from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Comment
@receiver(post_save, sender=Comment)
def on_comment_created(sender, instance: Comment, created: bool, **kwargs):
    if not created:
        return

    from .tasks import process_comment_created_event

    #process_comment_created_event.delay(instance.id)

