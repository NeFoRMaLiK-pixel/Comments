import io
from pathlib import Path

import bleach
from django.conf import settings
from django.core.cache import cache
from django.core.files.base import ContentFile
from PIL import Image

from .validators import validate_comment_xhtml

TOP_LEVEL_CACHE_KEY = "comments:top_level:{ordering}:{page}"


def sanitize_comment_html(text: str) -> str:
    validate_comment_xhtml(text)
    cleaned = bleach.clean(
        text,
        tags=settings.ALLOWED_COMMENT_TAGS,
        attributes=settings.ALLOWED_COMMENT_ATTRIBUTES,
        strip=True,
    )
    return cleaned


def normalize_uploaded_image(uploaded_file):
    image = Image.open(uploaded_file)
    image.load()

    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGB")

    max_w = settings.MAX_IMAGE_WIDTH
    max_h = settings.MAX_IMAGE_HEIGHT
    image.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)

    suffix = Path(uploaded_file.name).suffix.lower()
    format_map = {
        ".jpg": "JPEG",
        ".jpeg": "JPEG",
        ".gif": "GIF",
        ".png": "PNG",
    }
    img_format = format_map.get(suffix, "PNG")

    output = io.BytesIO()
    save_kwargs = {"format": img_format}
    if img_format == "JPEG":
        save_kwargs["quality"] = 90
        save_kwargs["optimize"] = True
    image.save(output, **save_kwargs)

    uploaded_file.seek(0)
    output.seek(0)
    filename = Path(uploaded_file.name).name
    return ContentFile(output.read(), name=filename)


def get_client_ip(request) -> str:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def invalidate_comment_cache() -> None:
    cache.clear()


def cache_key(ordering: str, page: int | str) -> str:
    return TOP_LEVEL_CACHE_KEY.format(ordering=ordering, page=page)
