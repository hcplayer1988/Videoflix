"""Admin configuration for upload app."""
 
from django.contrib import admin
from .models import FileUpload, Video
 
 
@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    """Admin configuration for the FileUpload model."""
 
    list_display = ['title', 'category', 'uploaded_at']
    list_filter = ['category']
    search_fields = ['title', 'description']
    ordering = ['-uploaded_at']
 
 
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin configuration for the Video model."""
 
    list_display = ['id', 'title', 'category', 'created_at']
    list_filter = ['category']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
