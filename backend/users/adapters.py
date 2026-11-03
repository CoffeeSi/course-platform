from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
from rest_framework_simplejwt.tokens import RefreshToken

from .cookies import set_auth_cookies


class JWTAccountAdapter(DefaultAccountAdapter):
    def post_login(self, request, user, **kwargs):
        response = super().post_login(request, user, **kwargs)
        if not user.is_active:
            return response

        # Trust only an address that Allauth has actually verified.
        if not user.is_email_verified and EmailAddress.objects.filter(
            user=user, email__iexact=user.email, verified=True
        ).exists():
            user.is_email_verified = True
            user.save(update_fields=["is_email_verified"])

        refresh = RefreshToken.for_user(user)
        set_auth_cookies(response, refresh.access_token, refresh)
        return response
