from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from allauth.socialaccount.models import SocialAccount
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .models import Profile, Post, Thread
from .notifications import send_notification_email
from .utils import extract_mentions

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
    
@receiver(post_save, sender=Post)
def notify_users_on_new_post(sender, instance, created, **kwargs):
    if not created:
        return
    thread = instance.thread
    author = instance.author
    mentioned_users = extract_mentions(instance.content)
    mentioned_ids = set(mentioned_users.values_list("id", flat=True))

    recipients = set()

    # thread creator
    if thread.creator != author and thread.creator.email:
        recipients.add(thread.creator.email)

    # other participants
    participants = (
    User.objects
    .filter(posts__thread=thread)
    .exclude(id__in=mentioned_ids)
    .exclude(id=author.id)
    .distinct()
)


    for user in participants:
        if user.email:
            recipients.add(user.email)
    subject = f"New reply in: {thread.title}"
    message = (
        f"{author.username} replied to the thread:\n\n"
        f"{thread.title}\n\n"
        f"{instance.content[:300]}...\n\n"
        f"Visit the forum to read more."
    )

    send_notification_email(subject, message, recipients)
    # mention notifications
    mentioned_users = extract_mentions(instance.content)

    for user in mentioned_users:
        if user == author:
            continue  # ignore self-mentions
        if not user.email:
            continue

        send_notification_email(
            subject=f"You were mentioned in '{thread.title}'",
            message=(
                f"{author.username} mentioned you in a reply.\n\n"
                f"Thread: {thread.title}\n\n"
                f"Excerpt:\n{instance.content[:300]}...\n\n"
                f"Visit the forum to reply."
            ),
            recipients=[user.email],
        )


@receiver(post_save, sender=Thread)
def notify_thread_lock_status(sender, instance, created, **kwargs):
    if created:
        return

    status = "locked" if instance.is_locked else "unlocked"

    user_ids = set(
    User.objects
    .filter(posts__thread=instance)
    .values_list("id", flat=True)
)
    
    user_ids.add(instance.creator_id)

    recipients = list(
        User.objects
        .filter(id__in=user_ids)
        .values_list("email", flat=True)
    )

    subject = f"Thread {status}: {instance.title}"
    message = (
        f"The thread '{instance.title}' has been {status} by a moderator.\n\n"
        f"If locked, replies are disabled."
    )

    send_notification_email(subject, message, recipients)

