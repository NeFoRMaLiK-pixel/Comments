from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

from django.conf import settings
from django.core.exceptions import ValidationError
from PIL import Image

ALLOWED_TAGS = set(settings.ALLOWED_COMMENT_TAGS)
ALLOWED_ATTRS = settings.ALLOWED_COMMENT_ATTRIBUTES


class StrictCommentHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._stack: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag not in ALLOWED_TAGS:
            raise ValidationError(f"Tag <{tag}> is not allowed.")

        allowed_attrs = set(ALLOWED_ATTRS.get(tag, []))
        attrs_map = dict(attrs)

        for name in attrs_map:
            if name not in allowed_attrs:
                raise ValidationError(f"Attribute '{name}' is not allowed for <{tag}>.")

        if tag == "a":
            href = attrs_map.get("href")
            if not href:
                raise ValidationError("Tag <a> requires attribute href.")
            parsed = urlparse(href)
            if parsed.scheme and parsed.scheme not in {"http", "https"}:
                raise ValidationError("Only http/https protocols are allowed in href.")

        self._stack.append(tag)

    def handle_endtag(self, tag):
        if tag not in ALLOWED_TAGS:
            raise ValidationError(f"Tag </{tag}> is not allowed.")
        if not self._stack:
            raise ValidationError(f"Closing tag </{tag}> has no matching opening tag.")
        opened = self._stack.pop()
        if opened != tag:
            raise ValidationError(f"Tag </{tag}> closes <{opened}>. XHTML nesting is invalid.")

    def handle_startendtag(self, tag, attrs):
        raise ValidationError("Self-closing tags are not supported in comments.")

    def close(self):
        super().close()
        if self._stack:
            raise ValidationError(f"Not all tags are closed: {', '.join(self._stack)}")


def validate_comment_xhtml(text: str) -> None:
    parser = StrictCommentHTMLParser()
    parser.feed(text or "")
    parser.close()


def detect_attachment_type(uploaded_file) -> str:
    if not uploaded_file:
        return "none"

    suffix = Path(uploaded_file.name).suffix.lower()

    if suffix in {".jpg", ".jpeg", ".gif", ".png"}:
        try:
            image = Image.open(uploaded_file)
            image.verify()
        except Exception as exc:
            raise ValidationError("Invalid image file.") from exc
        finally:
            uploaded_file.seek(0)
        return "image"

    if suffix == ".txt":
        if uploaded_file.size > settings.MAX_TEXT_FILE_BYTES:
            raise ValidationError("Text file must be <= 100KB.")
        try:
            uploaded_file.read().decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValidationError("Text file must be UTF-8 encoded.") from exc
        finally:
            uploaded_file.seek(0)
        return "text"

    raise ValidationError("Only JPG, GIF, PNG images or TXT files are allowed.")
