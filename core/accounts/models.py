from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    ssh_key = models.TextField(blank=True, help_text="Paste your SSH public key here.")
    sync_to_ldap = models.BooleanField(default=False, help_text="Sync this user to LDAP directory")
    ssh_enabled = models.BooleanField(default=True, help_text="Enable SSH Key management for this user")

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # Save may fail if profile is not created.
        if hasattr(instance, 'profile'):
            instance.profile.save()
