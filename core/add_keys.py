import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile

def assign_keys():
    # Read keys
    try:
        with open('/home/user4/.ssh/id_ed25519.pub', 'r') as f:
            key1 = f.read().strip()
        with open('/home/user4/.ssh/id_ed25519_user1.pub', 'r') as f:
            key2 = f.read().strip()
    except FileNotFoundError as e:
        print(f"Error reading key files: {e}")
        return

    try:
        # Assign to testuser
        testuser, created1 = User.objects.get_or_create(username="testuser")
        if created1:
            testuser.set_password("1234")
            testuser.save()
        
        if hasattr(testuser, 'profile'):
            testuser.profile.ssh_key = key1
            testuser.profile.save()
        else:
            UserProfile.objects.create(user=testuser, ssh_key=key1)
        print(f"✅ Added id_ed25519.pub to user 'testuser'.")

        # Assign to admin
        admin_user, created2 = User.objects.get_or_create(username="admin", defaults={'is_superuser': True, 'is_staff': True})
        if created2:
            admin_user.set_password("adminpassword")
            admin_user.save()

        if hasattr(admin_user, 'profile'):
            admin_user.profile.ssh_key = key2
            admin_user.profile.save()
        else:
            UserProfile.objects.create(user=admin_user, ssh_key=key2)
            
        print(f"✅ Added id_ed25519_user1.pub to user 'admin'.")
        
    except User.DoesNotExist as e:
        print(f"Error finding user: {e}")

if __name__ == '__main__':
    assign_keys()
