# Generated manually for the test task.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Comment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("username", models.CharField(max_length=64)),
                ("email", models.EmailField(max_length=254)),
                ("homepage", models.URLField(blank=True)),
                ("text_raw", models.TextField()),
                ("text_html", models.TextField()),
                ("attachment", models.FileField(blank=True, null=True, upload_to="attachments/")),
                (
                    "attachment_type",
                    models.CharField(
                        choices=[("none", "None"), ("image", "Image"), ("text", "Text")],
                        default="none",
                        max_length=10,
                    ),
                ),
                ("attachment_name", models.CharField(blank=True, max_length=255)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="comments.comment",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="CommentEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event_type", models.CharField(max_length=64)),
                ("payload", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "comment",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="events", to="comments.comment"),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="comment",
            index=models.Index(fields=["created_at"], name="comments_com_created_95f447_idx"),
        ),
        migrations.AddIndex(
            model_name="comment",
            index=models.Index(fields=["username"], name="comments_com_usernam_55f1de_idx"),
        ),
        migrations.AddIndex(
            model_name="comment",
            index=models.Index(fields=["email"], name="comments_com_email_9a6b90_idx"),
        ),
        migrations.AddIndex(
            model_name="comment",
            index=models.Index(fields=["parent", "created_at"], name="comments_com_parent__8ac8f6_idx"),
        ),
    ]
