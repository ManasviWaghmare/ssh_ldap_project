from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.ldap_sync import create_or_update_ldap_user

class Command(BaseCommand):
    help = 'Synchronizes all users with sync_to_ldap=True to the LDAP directory'

    def handle(self, *args, **options):
        users = User.objects.all()
        synced_count = 0
        failed_count = 0
        skipped_count = 0

        self.stdout.write(self.style.MIGRATE_HEADING(f'Starting bulk LDAP synchronization for {users.count()} users...'))

        for user in users:
            try:
                # Ensure user has a profile
                if hasattr(user, 'profile') and user.profile.sync_to_ldap:
                    result = create_or_update_ldap_user(user)
                    if result:
                        self.stdout.write(self.style.SUCCESS(f'Successfully synced user: {user.username}'))
                        synced_count += 1
                    else:
                        self.stdout.write(self.style.ERROR(f'Failed to sync user: {user.username} (LDAP error)'))
                        failed_count += 1
                else:
                    self.stdout.write(self.style.WARNING(f'Skipped user: {user.username} (Sync to LDAP disabled)'))
                    skipped_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error syncing user {user.username}: {str(e)}'))
                failed_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nSynchronization complete!\n'
            f'Synced: {synced_count}\n'
            f'Skipped: {skipped_count}\n'
            f'Failed: {failed_count}'
        ))
