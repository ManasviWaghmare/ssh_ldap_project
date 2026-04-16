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
    sys.exit(1)

dn = "uid=testuser,ou=people,dc=acwireless,dc=iucaa,dc=in"
try:
    # Attempt to modify the entry to add ldapPublicKey
    mod = [(ldap.MOD_ADD, 'objectClass', b'ldapPublicKey')]
    con.modify_s(dn, mod)
    print("Success: ldapPublicKey objectClass added.")
except ldap.LDAPError as e:
    print(f"Error adding ldapPublicKey: {e}")

con.unbind_s()
