"""Admin configuration for auth_app."""
 
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
 
User = get_user_model()
 
admin.site.unregister(User)
 
 
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for the User model."""
 
    list_display = ['email', 'username', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    search_fields = ['email', 'username']
    ordering = ['-date_joined']
    
    