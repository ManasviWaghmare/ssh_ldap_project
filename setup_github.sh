#!/bin/bash

# Check if a URL was provided as an argument
GITHUB_URL=$1

if [ -z "$GITHUB_URL" ]; then
    echo "Usage: ./setup_github.sh <YOUR_GITHUB_REPO_URL>"
    echo "Example: ./setup_github.sh https://github.com/username/ssh_ldap_project.git"
    exit 1
fi

# Initialize git if not already initialized
if [ ! -d ".git" ]; then
    git init
    echo "Initialized empty Git repository."
fi

# Add the remote
git remote add origin "$GITHUB_URL" 2>/dev/null || git remote set-url origin "$GITHUB_URL"
echo "Remote 'origin' set to $GITHUB_URL"

# Stage all files
git add .

# Create the initial commit
git commit -m "Initial commit: SSH LDAP Project with Django backend and LDAP config"

# Push to GitHub
# Note: This will push to the 'main' branch. If you use 'master', change it accordingly.
git branch -M main
git push -u origin main

echo "Done! Your project should now be on GitHub."
