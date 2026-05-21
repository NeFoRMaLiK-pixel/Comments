from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class PreviewApiTests(APITestCase):
    def test_preview_returns_sanitized_html(self):
        response = self.client.post(
            reverse("comment-preview"),
            {"text": "<strong>ok</strong> <script>bad()</script>"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_preview_accepts_valid_markup(self):
        response = self.client.post(
            reverse("comment-preview"),
            {"text": '<a href="https://example.com" title="ex">link</a>'},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("preview_html", response.data)
