from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from main.models.models import Profile


@receiver(post_save, sender=User)
def user_created(sender, instance, created, **kwargs):
    """
    Creates a new Profile instance when a User is created.
    """
    if created:
        Profile.create(user=instance)
