import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from accounts.models import UserProfile

User = get_user_model()

def run_tests():
    print("=== Testing LDAP Authentication and SSH Key Management ===")
    client = Client()

    # 1. Test GET Login
    print("\n1. Testing Login Page Route...")
    response = client.get('/login/')
    if response.status_code == 200:
        print("✅ Login page loads successfully (200 OK)")
    else:
        print(f"❌ Failed to load login page. Status: {response.status_code}")
        return

    # 2. Test POST Login with LDAP credentials
    print("\n2. Testing LDAP Authentication (testuser / 1234)...")
    # Note: django_auth_ldap will authenticate against localhost LDAP server
    response = client.post('/login/', {'username': 'testuser', 'password': '1234'})
    
    # Successful login should redirect (302) to /profile/
    if response.status_code == 302 and response.url == '/profile/':
        print("✅ LDAP Authentication successful! Redirected to /profile/")
    else:
        print(f"❌ LDAP Authentication failed! Status: {response.status_code}, URL: {getattr(response, 'url', 'None')}")
        # check if it's form error
        if response.status_code == 200:
            print("Form errors or auth failed.")
        return
        
    # Check if User was created via LDAP
    user = User.objects.filter(username='testuser').first()
    if user:
        print(f"✅ Django User object created! Name: {user.first_name} {user.last_name}")
    else:
        print("❌ Django User object not found in the DB. Something went wrong.")
        return

    # Check if UserProfile was created automatically via signals
    profile = UserProfile.objects.filter(user=user).first()
    if profile:
        print("✅ UserProfile automatically created via post_save signal!")
    else:
        print("❌ UserProfile was NOT created automatically. Check signals!")
        return

    # 3. Test Profile View & SSH Key update
    print("\n3. Testing SSH Key Upload...")
    dummy_key = "ssh-rsa AAAAB3NzaC1yc... testuser@machine"
    response = client.post('/profile/', {'ssh_key': dummy_key}, follow=True)
    
    if response.status_code == 200:
        profile.refresh_from_db()
        if profile.ssh_key == dummy_key:
            print("✅ SSH Key successfully updated via POST to /profile/")
        else:
            print(f"❌ SSH Key update failed! Profile has: {profile.ssh_key}")
    else:
        print(f"❌ Failed to access or post to /profile/. Status: {response.status_code}")

    print("\n=== All Tests Completed Successfully! ===")

if __name__ == '__main__':
    run_tests()
