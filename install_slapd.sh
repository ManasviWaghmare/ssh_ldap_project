#!/bin/bash
export DEBIAN_FRONTEND=noninteractive

# Pre-seed the configuration for slapd
sudo debconf-set-selections <<EOF
slapd slapd/domain string acwireless.iucaa.in
slapd slapd/internal/adminpw password adminpassword
slapd slapd/internal/adminpw_again password adminpassword
slapd slapd/purge_old_database boolean true
slapd slapd/no_configuration boolean false
EOF

# Install slapd and ldap-utils
sudo apt-get update
sudo apt-get install -y slapd ldap-utils

# Verify the service
systemctl status slapd --no-pager
