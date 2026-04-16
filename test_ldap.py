import os
import django
import sys
import ldap
import ldap.modlist as modlist

sys.path.append('/home/user4/Downloads/ssh_ldap_project/core')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from accounts.ldap_sync import get_ldap_connection

con = get_ldap_connection()
if not con:
    print("Failed to connect")
    sys.exit(1)

# just test adding ldapPublicKey objectClass to a test user if one exists or search for an existing user
results = con.search_s("ou=people,dc=acwireless,dc=iucaa,dc=in", ldap.SCOPE_SUBTREE, "(objectClass=inetOrgPerson)")
if results:
    dn = results[0][0]
    entry = results[0][1]
    print(f"Found {dn}")
    print(entry)
else:
    print("No users found")
con.unbind_s()
