from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .captcha import verify_captcha
from .models import Comment
from .services import get_client_ip, normalize_uploaded_image, sanitize_comment_html
from .validators import detect_attachment_type


class CommentTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    attachment_url = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            "id",
            "parent",
            "username",
            "email",
            "homepage",
            "text_html",
            "attachment_type",
            "attachment_name",
            "attachment_url",
            "created_at",
            "children",
        )

    def get_children(self, obj):
        nested = obj.children.all().order_by("created_at")
        return CommentTreeSerializer(nested, many=True, context=self.context).data

    def get_attachment_url(self, obj):
        if not obj.attachment:
            return ""
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.attachment.url)
        return obj.attachment.url


class CommentCreateSerializer(serializers.ModelSerializer):
    text = serializers.CharField(write_only=True)
    captcha_key = serializers.CharField(write_only=True)
    captcha_value = serializers.CharField(write_only=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "parent",
            "username",
            "email",
            "homepage",
            "text",
            "attachment",
            "captcha_key",
            "captcha_value",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def validate(self, attrs):
        captcha_key = attrs.pop("captcha_key", "")
        captcha_value = attrs.pop("captcha_value", "")

        if not verify_captcha(captcha_key, captcha_value):
            raise serializers.ValidationError({"captcha_value": "CAPTCHA is invalid or expired."})

        raw_text = attrs.get("text", "")
        try:
            text_html = sanitize_comment_html(raw_text)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"text": exc.messages}) from exc

        attachment = attrs.get("attachment")
        attachment_type = detect_attachment_type(attachment)

        attrs["_text_html"] = text_html
        attrs["_attachment_type"] = attachment_type
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")

        raw_text = validated_data.pop("text")
        text_html = validated_data.pop("_text_html")
        attachment_type = validated_data.pop("_attachment_type")
        attachment = validated_data.pop("attachment", None)

        comment = Comment(
            text_raw=raw_text,
            text_html=text_html,
            attachment_type=attachment_type,
            attachment_name=attachment.name if attachment else "",
            user_agent=(request.META.get("HTTP_USER_AGENT", "")[:255] if request else ""),
            ip_address=(get_client_ip(request) if request else ""),
            **validated_data,
        )

        if attachment and attachment_type == Comment.AttachmentType.IMAGE:
            normalized = normalize_uploaded_image(attachment)
            comment.attachment.save(normalized.name, normalized, save=False)
        elif attachment:
            comment.attachment = attachment

        comment.save()
        return comment


class PreviewSerializer(serializers.Serializer):
    text = serializers.CharField()

    def validate_text(self, value):
        try:
            return sanitize_comment_html(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc
