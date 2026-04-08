from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'sync_to_ldap', 'ssh_enabled', 'ssh_key_preview')
    list_filter = ('sync_to_ldap', 'ssh_enabled')
    search_fields = ('user__username', 'user__email')

    def ssh_key_preview(self, obj):
        if obj.ssh_key:
            return obj.ssh_key[:50] + "..." if len(obj.ssh_key) > 50 else obj.ssh_key
        return "-"
    ssh_key_preview.short_description = 'SSH Key'
