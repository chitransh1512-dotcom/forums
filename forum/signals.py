from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from allauth.socialaccount.models import SocialAccount
from .models import Profile

@receiver(user_signed_up)
def populate_profile(request, user, **kwargs):
    full_name = user.get_full_name()
    avatar = ""

    try:
        social = SocialAccount.objects.get(user=user, provider="google")
        full_name = social.extra_data.get("name", full_name)
        avatar = social.extra_data.get("picture", "")
    except SocialAccount.DoesNotExist:
        pass

    Profile.objects.create(
        user=user,
        full_name=full_name,
        avatar=avatar
    )
    

