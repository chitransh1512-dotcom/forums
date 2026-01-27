import re
from django.contrib.auth.models import User

MENTION_REGEX = r'@(\w+)'

def extract_mentions(text):
    """
    Returns queryset of Users mentioned via @username
    """
    usernames = set(re.findall(MENTION_REGEX, text))
    return User.objects.filter(username__in=usernames)
