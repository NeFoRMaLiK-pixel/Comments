from django.core.validators import RegexValidator
from django.db import models

USERNAME_VALIDATOR = RegexValidator(
    regex=r"^[A-Za-z0-9]+$",
    message="User Name can contain only latin letters and digits.",
)


class Comment(models.Model):
    class AttachmentType(models.TextChoices):
        NONE = "none", "None"
        IMAGE = "image", "Image"
        TEXT = "text", "Text"

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
    )
    username = models.CharField(max_length=64, validators=[USERNAME_VALIDATOR])
    email = models.EmailField()
    homepage = models.URLField(blank=True)
    text_raw = models.TextField()
    text_html = models.TextField()

    attachment = models.FileField(upload_to="attachments/", null=True, blank=True)
    attachment_type = models.CharField(
        max_length=10,
        choices=AttachmentType.choices,
        default=AttachmentType.NONE,
    )
    attachment_name = models.CharField(max_length=255, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["username"]),
            models.Index(fields=["email"]),
            models.Index(fields=["parent", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.username}: {self.id}"


class CommentEvent(models.Model):
    event_type = models.CharField(max_length=64)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="events")
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.event_type} ({self.comment_id})"
