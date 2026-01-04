from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.http import HttpResponse
from forums.validators import validate_bits_pilani_email


class RestrictedDomainSocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        email = sociallogin.user.email

        try:
            validate_bits_pilani_email(email)
        except Exception:
            raise ImmediateHttpResponse(
                HttpResponse(
                    """
                    <h2>Google Sign-in Not Allowed</h2>
                    <p>
                        Only BITS Pilani student email addresses are allowed.
                    </p>
                    <p>
                        Please use your official college Google account
                        (fYYYYRRRR@pilani.bits-pilani.ac.in).
                    </p>
                    <a href="/accounts/login/">Back to Login</a>
                    """,
                    status=403,
                )
            )
