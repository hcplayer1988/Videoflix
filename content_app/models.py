"""Models for content app."""
 
from django.db import models
 
 
class Video(models.Model):
    """Represents a video with metadata."""
 
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    category = models.CharField(max_length=100, blank=True)
 
    def __str__(self):
        return self.title