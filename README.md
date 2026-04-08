# SSH LDAP Management System

A robust, enterprise-ready management system for handling centralized user authentication and SSH public keys using **Django**, **OpenLDAP**, and **MySQL**.

## 🚀 Key Features

- **Centralized Authentication**: Integrated with OpenLDAP using `django-auth-ldap`.
- **MySQL Persistence**: Robust data storage for user profiles and application state.
- **SSH Key Portal**: Users can self-manage their SSH public keys via a modern dashboard.
- **SSH Integration**: Ready-to-use endpoint for OpenSSH's `AuthorizedKeysCommand`.
- **Administrative Control**: Superuser dashboard for managing all users and bulk LDAP syncing.
- **Automated Deployment**: Includes shell scripts for non-interactive OpenLDAP installation and configuration.

## 🏗 System Architecture

The system acts as a bridge between your web interface and your infrastructure's identity layer.

1.  **Frontend**: User/Admin Dashboard (Django Templates).
2.  **Backend**: Django Application (`core` directory).
3.  **Database**: MySQL for persistence of user profiles and local settings.
4.  **Identity Provider**: OpenLDAP for centralized authentication.
5.  **SSH Service**: Servers can poll the Django API to retrieve authorized keys dynamically.

---

## 🛠 Installation & Setup

### 1. Prerequisites
Ensure you have the following installed on your system:
- Python 3.8+
- MySQL Server 8.0+
- OpenLDAP (`slapd`)
- Development headers for LDAP and SASL (e.g., `libldap2-dev libsasl2-dev` on Ubuntu)

### 2. LDAP Setup
Use the provided script to install and seed the LDAP directory:
```bash
chmod +x install_slapd.sh
./install_slapd.sh
```
The default configuration uses:
- **Domain**: `acwireless.iucaa.in`
- **Admin DN**: `cn=admin,dc=acwireless,dc=iucaa,dc=in`
- **Admin Password**: `adminpassword`

Load the base schema:
```bash
ldapadd -x -D "cn=admin,dc=acwireless,dc=iucaa,dc=in" -W -f base.ldif
ldapadd -x -D "cn=admin,dc=acwireless,dc=iucaa,dc=in" -W -f user.ldif
```

### 3. Database Setup (MySQL)
Create the database and user as specified in `core/settings.py`:
```sql
CREATE DATABASE Manasvi CHARACTER SET utf8mb4;
CREATE USER 'Manasvi'@'localhost' IDENTIFIED BY 'Kiran@2210';
GRANT ALL PRIVILEGES ON Manasvi.* TO 'Manasvi'@'localhost';
FLUSH PRIVILEGES;
```

### 4. Backend Configuration
1. **Navigate to the core directory**:
   ```bash
   cd core
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```
4. **Create a Superuser**:
   ```bash
   python manage.py createsuperuser
   ```
5. **Start the server**:
   ```bash
   python manage.py runserver
   ```

---

## 🔒 SSH Integration

To integrate this system with your OpenSSH server, add the following to your `/etc/ssh/sshd_config`:

```ssh
AuthorizedKeysCommand /usr/bin/curl -s http://your-domain.com/authorized_keys/%u/
AuthorizedKeysCommandUser nobody
```

This configuration tells OpenSSH to fetch the public keys for any connecting user directly from the Django endpoint.

---

## 📁 Project Structure

- `core/`: Main Django application.
  - `accounts/`: Application logic for user management and LDAP sync.
  - `core/`: Project-wide settings and URLs.
- `ldap_config/`: Raw LDIF files and search configurations.
- `setup_github.sh`: Helper script for git operations.
- `LICENSE`: MIT License.

## 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.

## 🤝 Contributing

Contributions are welcome! Please follow the standard fork-and-pull-request workflow. Ensure your code complies with PEP 8 standards.

---
*Maintained by ManasviWaghmare*
