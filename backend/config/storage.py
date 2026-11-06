from django.conf import settings
from django.utils.functional import cached_property
from storages.backends.s3 import S3Storage


class BrowserURLS3Storage(S3Storage):
    """Use the internal endpoint for I/O and the public endpoint for signed URLs."""

    @cached_property
    def public_storage(self):
        return S3Storage(
            endpoint_url=settings.AWS_S3_PUBLIC_ENDPOINT_URL,
            addressing_style="path",
        )

    def url(self, name, parameters=None, expire=None, http_method=None):
        return self.public_storage.url(
            name, parameters=parameters, expire=expire, http_method=http_method
        )
