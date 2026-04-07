"""Models for upload app."""
 
import os
import shutil
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings
 
 
class Video(models.Model):
    """Represents an uploaded video with metadata and HLS conversion state."""
 
    file = models.FileField(upload_to='uploads/')
    title = models.CharField(max_length=255, default='')
    description = models.TextField(blank=True, default='')
    category = models.CharField(max_length=100, blank=True, default='')
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ['-created_at']
 
    def __str__(self):
        return self.title
 
 
@receiver(post_delete, sender=Video)
def delete_video_files(sender, instance, **kwargs):
    """Deletes raw upload, thumbnail and HLS files when a Video is deleted."""
    if instance.file and os.path.isfile(instance.file.path):
        os.remove(instance.file.path)
    if instance.thumbnail and os.path.isfile(instance.thumbnail.path):
        os.remove(instance.thumbnail.path)
    hls_dir = os.path.join(settings.MEDIA_ROOT, 'videos', str(instance.pk))
    if os.path.isdir(hls_dir):
        shutil.rmtree(hls_dir)

