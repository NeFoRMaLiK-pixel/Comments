from django.core.cache import cache
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .captcha import create_captcha
from .models import Comment
from .serializers import CommentCreateSerializer, CommentTreeSerializer, PreviewSerializer
from .services import cache_key


class CommentListCreateView(ListCreateAPIView):
    permission_classes = [AllowAny]
    filterset_fields = []
    ordering_fields = ["username", "email", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return (
            Comment.objects.filter(parent__isnull=True)
            .select_related("parent")
            .prefetch_related("children", "children__children", "children__children__children")
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CommentCreateSerializer
        return CommentTreeSerializer

    def list(self, request, *args, **kwargs):
        ordering = request.query_params.get("ordering", "-created_at")
        if ordering not in {"username", "-username", "email", "-email", "created_at", "-created_at"}:
            ordering = "-created_at"

        page = request.query_params.get("page", "1")
        key = cache_key(ordering, page)
        cached = cache.get(key)
        if cached is not None:
            return Response(cached)

        response = super().list(request, *args, **kwargs)
        cache.set(key, response.data, timeout=120)
        return response


class CaptchaView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(create_captcha())


class CommentPreviewView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PreviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"preview_html": serializer.validated_data["text"]}, status=status.HTTP_200_OK)
