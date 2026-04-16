from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='login', permanent=False), name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('keys/<str:username>/', views.authorized_keys, name='authorized_keys'),

<<<<<<< HEAD
=======
    # SSH Key Management
    path('ssh-keys/add/', views.add_ssh_key, name='add_ssh_key'),
    path('ssh-keys/validate-ajax/', views.validate_ssh_key_ajax, name='validate_ssh_key_ajax'),
    path('ssh-keys/<int:key_id>/edit/', views.edit_ssh_key, name='edit_ssh_key'),
    path('ssh-keys/<int:key_id>/delete/', views.delete_ssh_key, name='delete_ssh_key'),

>>>>>>> 1126c2b (Added SSH key validation with cryptographic checks)
    # User Management (Staff only)
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/<int:user_id>/edit/', views.update_user, name='update_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('users/sync-all-ldap/', views.sync_all_to_ldap, name='sync_all_to_ldap'),
    path('ldap-status/', views.ldap_status, name='ldap_status'),
]
