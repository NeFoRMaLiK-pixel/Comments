from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase

from comments.validators import detect_attachment_type, validate_comment_xhtml


class XHTMLValidationTests(SimpleTestCase):
    def test_accepts_allowed_tags(self):
        validate_comment_xhtml('<strong>Hello</strong> <i>world</i> <code>x = 1</code>')

    def test_rejects_unclosed_tags(self):
        with self.assertRaises(ValidationError):
            validate_comment_xhtml('<strong>broken')

    def test_rejects_unknown_tag(self):
        with self.assertRaises(ValidationError):
            validate_comment_xhtml('<script>alert(1)</script>')


class AttachmentValidationTests(SimpleTestCase):
    def test_rejects_unknown_extension(self):
        attachment = SimpleUploadedFile('bad.pdf', b'fake-data')
        with self.assertRaises(ValidationError):
            detect_attachment_type(attachment)

    def test_rejects_txt_over_limit(self):
        attachment = SimpleUploadedFile('large.txt', b'a' * (100 * 1024 + 1))
        with self.assertRaises(ValidationError):
            detect_attachment_type(attachment)
