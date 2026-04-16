import ldap
import ldap.modlist as modlist
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def get_ldap_connection():
    try:
        con = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
        con.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
        return con
    except ldap.LDAPError as e:
        logger.error(f"Failed to connect to LDAP: {e}")
        return None

def create_or_update_ldap_user(user, raw_password=None):
    """
    Creates or updates a user in the LDAP directory based on a Django User.
    This does NOT run automatically on every save to avoid loops with django-auth-ldap.
    """
    con = get_ldap_connection()
    if not con:
        return False
        
    username = user.username
    dn = f"uid={username},ou=people,dc=acwireless,dc=iucaa,dc=in"
    
    # Determine attributes
    sn = user.last_name if user.last_name else username
    cn = f"{user.first_name} {user.last_name}".strip() if user.first_name else username
    
    attrs = {
        'objectClass': [b'inetOrgPerson', b'top'],
        'uid': [username.encode('utf-8')],
        'sn': [sn.encode('utf-8')],
        'cn': [cn.encode('utf-8')],
    }
    
    if user.first_name:
        attrs['givenName'] = [user.first_name.encode('utf-8')]
    if user.email:
        attrs['mail'] = [user.email.encode('utf-8')]
    if raw_password:
        attrs['userPassword'] = [raw_password.encode('utf-8')]
    # SSH Keys handling
    if hasattr(user, 'profile') and user.profile.ssh_enabled:
        ssh_keys = [k.key_content.encode('utf-8') for k in user.ssh_keys.all()]
        if ssh_keys:
            attrs['objectClass'].append(b'ldapPublicKey')
            attrs['sshPublicKey'] = ssh_keys

    try:
        # Check if user exists
        results = con.search_s(dn, ldap.SCOPE_BASE)
        # Exists, perform modify
        existing_entry = results[0][1]
        modifications = []
        
        # Compare and update objectClass
        current_oc = existing_entry.get('objectClass', [])
        new_oc = attrs['objectClass']
        if set(current_oc) != set(new_oc):
            modifications.append((ldap.MOD_REPLACE, 'objectClass', new_oc))
            
        # Compare and update simple attributes
        for attr in ['sn', 'cn', 'givenName', 'mail', 'userPassword', 'sshPublicKey']:
            new_val = attrs.get(attr, [])
            old_val = existing_entry.get(attr, [])
            if set(new_val) != set(old_val):
                if new_val:
                    modifications.append((ldap.MOD_REPLACE, attr, new_val))
                elif old_val:
                    modifications.append((ldap.MOD_DELETE, attr, None))
                    
        if modifications:
            con.modify_s(dn, modifications)
            logger.info(f"Successfully updated user {username} in LDAP.")
        else:
            logger.info(f"User {username} already up to date in LDAP.")
        return True

    except ldap.NO_SUCH_OBJECT:
        # Doesn't exist, create
        if not raw_password:
            # Need a password for a new LDAP user!
            attrs['userPassword'] = [b'changeme123']
            
        ldif = modlist.addModlist(attrs)
        try:
            con.add_s(dn, ldif)
            logger.info(f"Successfully created user {username} in LDAP via Django.")
            return True
        except ldap.LDAPError as e:
            logger.error(f"Failed to add user {username} to LDAP: {e}")
            return False
            
    finally:
        con.unbind_s()
        
    return False

def get_all_ldap_users():
    """
    Fetches all user entries from the LDAP directory.
    """
    con = get_ldap_connection()
    if not con:
        return []

    base_dn = "ou=people,dc=acwireless,dc=iucaa,dc=in"
    search_filter = "(objectClass=inetOrgPerson)"
    
    try:
        results = con.search_s(base_dn, ldap.SCOPE_SUBTREE, search_filter)
        user_list = []
        for dn, entry in results:
            if isinstance(entry, dict):
                user_data = {
                    'dn': dn,
                    'username': entry.get('uid', [b''])[0].decode('utf-8'),
                    'cn': entry.get('cn', [b''])[0].decode('utf-8'),
                    'sn': entry.get('sn', [b''])[0].decode('utf-8'),
                    'givenName': entry.get('givenName', [b''])[0].decode('utf-8'),
                    'mail': entry.get('mail', [b''])[0].decode('utf-8'),
                }
                user_list.append(user_data)
        return user_list
    except ldap.LDAPError as e:
        logger.error(f"Failed to fetch LDAP users: {e}")
        return []
    finally:
        con.unbind_s()

def delete_ldap_user(username):
    con = get_ldap_connection()
    if not con:
        return False
        
    dn = f"uid={username},ou=people,dc=acwireless,dc=iucaa,dc=in"
    try:
        con.delete_s(dn)
        logger.info(f"Deleted user {username} from LDAP.")
        return True
    except ldap.NO_SUCH_OBJECT:
        return True
    except ldap.LDAPError as e:
        logger.error(f"Failed to delete user {username} from LDAP: {e}")
        return False
    finally:
        con.unbind_s()
