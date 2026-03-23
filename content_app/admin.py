"""Admin configuration for content app."""
 
from django.contrib import admin
from content_app.models import Video
 
 
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin configuration for the Video model."""
 
    list_display = ['id', 'title', 'category', 'created_at']
    list_filter = ['category']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
