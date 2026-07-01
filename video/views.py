import boto3
from botocore.config import Config
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from urllib.parse import urlparse


class VideoURLView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        raw_video_key = request.query_params.get("key")
        if not raw_video_key:
            return Response({"error": "Key is required"}, status=400)

        parsed_url = urlparse(raw_video_key)
        video_key = parsed_url.path

        video_key = video_key.lstrip("/")

        bucket_prefix = f"{settings.AWS_STORAGE_BUCKET_NAME}/"
        if video_key.startswith(bucket_prefix):
            video_key = video_key[len(bucket_prefix) :]

        if video_key.startswith("api/v1/download-shared-object/"):
            video_key = video_key.replace("api/v1/download-shared-object/", "")

        my_config = Config(signature_version="s3v4", s3={"addressing_style": "path"})

        s3 = boto3.client(
            "s3",
            endpoint_url=getattr(
                settings, "AWS_S3_PUBLIC_ENDPOINT_URL", settings.AWS_S3_ENDPOINT_URL
            ),
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=my_config,
        )

        try:
            url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": video_key},
                ExpiresIn=3600,
            )
            return Response({"url": url})
        except Exception as e:
            return Response(
                {"error": f"Failed to generate secure URL: {str(e)}"}, status=500
            )
