import base64
import io
import secrets
import string

from django.conf import settings
from PIL import Image, ImageDraw, ImageFont

from .services import safe_cache_delete, safe_cache_get, safe_cache_set

CAPTCHA_PREFIX = "captcha:"


def _captcha_key() -> str:
    return secrets.token_urlsafe(16)


def _captcha_value() -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(settings.CAPTCHA_LENGTH))


def _build_image(value: str) -> str:
    image = Image.new("RGB", (190, 60), (250, 250, 255))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    for x in range(0, 190, 12):
        draw.line((x, 0, x + 15, 60), fill=(230, 230, 240), width=1)

    draw.text((20, 20), value, font=font, fill=(35, 35, 35))

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def create_captcha() -> dict:
    key = _captcha_key()
    value = _captcha_value()
    safe_cache_set(f"{CAPTCHA_PREFIX}{key}", value.lower(), timeout=settings.CAPTCHA_TTL_SECONDS)

    return {
        "key": key,
        "image": _build_image(value),
        "ttl": settings.CAPTCHA_TTL_SECONDS,
    }


def verify_captcha(key: str, value: str) -> bool:
    stored = safe_cache_get(f"{CAPTCHA_PREFIX}{key}")
    if not stored:
        return False

    ok = stored == (value or "").lower().strip()
    if ok:
        safe_cache_delete(f"{CAPTCHA_PREFIX}{key}")
    return ok
