# SSH LDAP Project

A secure management system for handling SSH keys and user authentication using LDAP and Django.

## Features

- **LDAP Integration**: Centralized user authentication and management.
- **SSH Key Management**: Easily add and manage SSH keys for LDAP users.
- **Django Backend**: Modern web interface and API for administrative tasks.
- **Automated Setup**: Scripts included for installing LDAP (`slapd`) and configuring the environment.

## Project Structure

```text
.
├── core/                   # Django project root
│   ├── core/               # Project settings and configuration
│   ├── accounts/           # User and LDAP account management
│   └── manage.py           # Django management script
├── ldap_config/            # Configuration files for OpenLDAP
├── base.ldif, user.ldif    # LDAP schema and initial data
├── install_slapd.sh        # Script to install and configure OpenLDAP
└── README.md               # This file
```

## Setup Instructions

### 1. Prerequisites
- Python 3.8+
- OpenLDAP (`slapd`)
- Django 4.x

### 2. Install LDAP
Run the provided installation script:
```bash
chmod +x install_slapd.sh
./install_slapd.sh
```

### 3. Backend Setup
Navigate to the `core/` directory and install dependencies:
```bash
cd core
# It is recommended to use a virtual environment
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 4. LDAP Configuration
Load the initial LDIF files:
```bash
ldapadd -x -D "cn=admin,dc=example,dc=com" -W -f base.ldif
ldapadd -x -D "cn=admin,dc=example,dc=com" -W -f user.ldif
```

## Contributing
Please follow standard git flow. Ensure that sensitive configuration files are ignored by `.gitignore`.

## License
MIT
