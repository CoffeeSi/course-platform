from django.conf import settings

ACCESS_COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"

def set_auth_cookies(response, access, refresh=None):
    options = {
        "httponly": settings.JWT_AUTH_COOKIE_HTTP_ONLY,
        "secure": settings.JWT_AUTH_COOKIE_SECURE,
        "samesite": settings.JWT_AUTH_COOKIE_SAMESITE,
        "path": settings.JWT_AUTH_COOKIE_PATH,
    }
    response.set_cookie(
        ACCESS_COOKIE_NAME,
        str(access),
        max_age=int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
        **options,
    )
    if refresh is not None:
        response.set_cookie(
            REFRESH_COOKIE_NAME,
            str(refresh),
            max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
            **options,
        )


def clear_auth_cookies(response):
    for name in (ACCESS_COOKIE_NAME, REFRESH_COOKIE_NAME):
        response.delete_cookie(
            name,
            path=settings.JWT_AUTH_COOKIE_PATH,
            samesite=settings.JWT_AUTH_COOKIE_SAMESITE,
        )
