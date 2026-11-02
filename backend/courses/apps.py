from django.apps import AppConfig


class CoursesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "courses"

    def ready(self):
        from django.conf import settings

        if getattr(settings, "USE_SEAWEEDFS", False):
            import logging

            import boto3
            from botocore.exceptions import ClientError

            logger = logging.getLogger(__name__)
            try:
                s3 = boto3.client(
                    "s3",
                    endpoint_url=settings.SEAWEEDFS_ENDPOINT,
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                )
                bucket_name = settings.AWS_STORAGE_BUCKET_NAME
                try:
                    s3.head_bucket(Bucket=bucket_name)
                except ClientError as e:
                    error_code = e.response["Error"].get("Code")
                    # 404 means bucket does not exist, so we create it
                    if (
                        error_code == "404"
                        or e.response["ResponseMetadata"]["HTTPStatusCode"] == 404
                    ):
                        s3.create_bucket(Bucket=bucket_name)
                        logger.info(f"Bucket '{bucket_name}' created successfully.")
            except Exception as e:
                logger.warning(f"WARN Could not check/create S3 bucket on startup: {e}")
