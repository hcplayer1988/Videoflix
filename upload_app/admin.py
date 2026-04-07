"""Admin configuration for upload app."""
 
from django.contrib import admin
from .models import Video
 
 
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin configuration for the Video model."""
 
    list_display = ['title', 'category', 'created_at']
    list_filter = ['category']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
 
 
