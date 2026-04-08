from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, authenticate
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import UserProfile
from .ldap_sync import create_or_update_ldap_user, delete_ldap_user


def is_admin(user):
    return user.is_superuser


@login_required
def profile(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.email = request.POST.get('email', '').strip()
        user.save()

        ssh_key = request.POST.get('ssh_key', '').strip()
        profile.ssh_key = ssh_key
        profile.save()

        # Sync to LDAP if enabled for this user
        if profile.sync_to_ldap:
            result = create_or_update_ldap_user(user)
            if result:
                messages.success(request, 'Profile and SSH key updated and synced to LDAP.')
            else:
                messages.warning(request, 'Profile updated locally, but LDAP sync failed.')
        else:
            messages.success(request, 'Your profile and SSH key have been updated successfully.')
        
        return redirect('profile')

    users = None
    if request.user.is_superuser:
        users = User.objects.select_related('profile').all().order_by('-date_joined')

    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'users': users
    })


def authorized_keys(request, username):
    """
    Endpoint for OpenSSH AuthorizedKeysCommand.
    Returns the SSH public key(s) for the requested user.
    """
    user = get_object_or_404(User, username=username)
    try:
        if not user.profile.ssh_enabled:
            return HttpResponse("", content_type="text/plain", status=200)
        ssh_key = user.profile.ssh_key
        if ssh_key:
            return HttpResponse(ssh_key, content_type="text/plain")
        else:
            return HttpResponse("", content_type="text/plain", status=200)
    except UserProfile.DoesNotExist:
        return HttpResponse("", content_type="text/plain", status=200)


# ─── User Management (Staff Only) ────────────────────────────────────────────

@login_required
@user_passes_test(is_admin)
def user_list(request):
    """List all users with their profile status."""
    users = User.objects.select_related('profile').all().order_by('-date_joined')
    return render(request, 'accounts/user_list.html', {'users': users})


@login_required
@user_passes_test(is_admin)
def add_user(request):
    """Create a new user with checkboxes for LDAP sync and SSH."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        ssh_key = request.POST.get('ssh_key', '').strip()
        sync_to_ldap = request.POST.get('sync_to_ldap') == 'on'
        ssh_enabled = request.POST.get('ssh_enabled') == 'on'

        if not username or not password:
            messages.error(request, 'Username and Password are required.')
            return render(request, 'accounts/user_form.html', {
                'form_title': 'Add New User',
                'form_data': request.POST,
            })

        if User.objects.filter(username=username).exists():
            messages.error(request, f'User "{username}" already exists.')
            return render(request, 'accounts/user_form.html', {
                'form_title': 'Add New User',
                'form_data': request.POST,
            })

        # Create Django user
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )

        # Update profile (auto-created by signal)
        profile = user.profile
        profile.ssh_key = ssh_key
        profile.sync_to_ldap = sync_to_ldap
        profile.ssh_enabled = ssh_enabled
        profile.save()

        # Sync to LDAP if checked
        if sync_to_ldap:
            result = create_or_update_ldap_user(user, raw_password=password)
            if result:
                messages.success(request, f'User "{username}" created and synced to LDAP.')
            else:
                messages.warning(request, f'User "{username}" created but LDAP sync failed.')
        else:
            messages.success(request, f'User "{username}" created successfully.')

        return redirect('user_list')

    return render(request, 'accounts/user_form.html', {
        'form_title': 'Add New User',
    })


@login_required
@user_passes_test(is_admin)
def update_user(request, user_id):
    """Edit an existing user's details and toggle checkboxes."""
    target_user = get_object_or_404(User, pk=user_id)
    try:
        profile = target_user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=target_user)

    if request.method == 'POST':
        target_user.first_name = request.POST.get('first_name', '').strip()
        target_user.last_name = request.POST.get('last_name', '').strip()
        target_user.email = request.POST.get('email', '').strip()

        new_password = request.POST.get('password', '').strip()
        if new_password:
            target_user.set_password(new_password)

        target_user.save()

        profile.ssh_key = request.POST.get('ssh_key', '').strip()
        profile.sync_to_ldap = request.POST.get('sync_to_ldap') == 'on'
        profile.ssh_enabled = request.POST.get('ssh_enabled') == 'on'
        profile.save()

        # Sync to LDAP if checked
        if profile.sync_to_ldap:
            result = create_or_update_ldap_user(target_user, raw_password=new_password if new_password else None)
            if result:
                messages.success(request, f'User "{target_user.username}" updated and synced to LDAP.')
            else:
                messages.warning(request, f'User "{target_user.username}" updated but LDAP sync failed.')
        else:
            messages.success(request, f'User "{target_user.username}" updated successfully.')

        return redirect('user_list')

    return render(request, 'accounts/user_form.html', {
        'form_title': f'Edit User: {target_user.username}',
        'target_user': target_user,
        'profile': profile,
        'is_edit': True,
    })


@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    """Delete a user, also remove from LDAP if synced."""
    target_user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        username = target_user.username

        # Remove from LDAP if they were synced
        try:
            if target_user.profile.sync_to_ldap:
                delete_ldap_user(username)
        except UserProfile.DoesNotExist:
            pass

        target_user.delete()
        messages.success(request, f'User "{username}" has been deleted.')
        return redirect('user_list')

@login_required
@user_passes_test(is_admin)
def sync_all_to_ldap(request):
    """Trigger a bulk LDAP synchronization for all users."""
    users = User.objects.all()
    synced_count = 0
    failed_count = 0
    skipped_count = 0

    for user in users:
        if hasattr(user, 'profile') and user.profile.sync_to_ldap:
            result = create_or_update_ldap_user(user)
            if result:
                synced_count += 1
            else:
                failed_count += 1
        else:
            skipped_count += 1

    if failed_count > 0:
        messages.warning(request, f'Synchronization complete with errors. Synced: {synced_count}, Skipped: {skipped_count}, Failed: {failed_count}')
    else:
        messages.success(request, f'All users successfully synchronized to LDAP. Sync: {synced_count}, Skip: {skipped_count}')
        
    return redirect('profile')


@login_required
def change_password(request):
    """Allow users to change their own password."""
    if request.method == 'POST':
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # Validate current password
        if not authenticate(username=request.user.username, password=current_password):
            messages.error(request, 'Your current password is incorrect.')
            return redirect('profile')

        # Validate new passwords match
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('profile')

        # Validate password length
        if len(new_password) < 6:
            messages.error(request, 'New password must be at least 6 characters long.')
            return redirect('profile')

        # Update password
        request.user.set_password(new_password)
        request.user.save()

        # Keep user logged in after password change
        update_session_auth_hash(request, request.user)

        # Sync to LDAP if enabled
        try:
            profile = request.user.profile
            if profile.sync_to_ldap:
                result = create_or_update_ldap_user(request.user, raw_password=new_password)
                if result:
                    messages.success(request, 'Password changed and synced to LDAP successfully.')
                else:
                    messages.warning(request, 'Password changed locally, but LDAP sync failed.')
            else:
                messages.success(request, 'Your password has been changed successfully.')
        except UserProfile.DoesNotExist:
            messages.success(request, 'Your password has been changed successfully.')

        return redirect('profile')

    return redirect('profile')


@login_required
@user_passes_test(is_admin)
def ldap_status(request):
    """View to display live content of the LDAP directory."""
    from .ldap_sync import get_all_ldap_users
    ldap_users = get_all_ldap_users()
    return render(request, 'accounts/ldap_status.html', {
        'ldap_users': ldap_users
    })
