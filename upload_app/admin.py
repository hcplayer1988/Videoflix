"""Admin configuration for upload app."""
 
from django.contrib import admin
from .models import FileUpload
 
 
@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    """Admin configuration for the FileUpload model."""
 
    list_display = ['title', 'category', 'uploaded_at']
    list_filter = ['category']
    search_fields = ['title', 'description']
    ordering = ['-uploaded_at']
