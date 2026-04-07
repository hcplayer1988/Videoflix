"""Signals for upload app."""
 
import django_rq
from django.db.models.signals import post_save
from django.dispatch import receiver
 
from upload_app.models import Video
from .tasks import convert_to_hls
 
 
@receiver(post_save, sender=Video)
def handle_video_upload(sender, instance, created, **kwargs):
    """Starts HLS conversion after a new Video is saved."""
    if not created:
        return
    queue = django_rq.get_queue('default')
    queue.enqueue(convert_to_hls, instance.id, instance.file.path)
            