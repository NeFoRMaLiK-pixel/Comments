from django.contrib import admin

from .models import Comment, CommentEvent


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "parent", "created_at")
    search_fields = ("username", "email", "text_html")
    list_filter = ("created_at",)


@admin.register(CommentEvent)
class CommentEventAdmin(admin.ModelAdmin):
    list_display = ("id", "event_type", "comment_id", "created_at")
    list_filter = ("event_type", "created_at")
