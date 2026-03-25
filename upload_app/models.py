"""Models for upload app."""
 
from django.db import models
 
 
class FileUpload(models.Model):
    """Represents an uploaded video file with metadata."""
 
    file = models.FileField(upload_to='uploads/')
    title = models.CharField(max_length=255, default='')
    description = models.TextField(blank=True, default='')
    category = models.CharField(max_length=100, blank=True, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return self.title
