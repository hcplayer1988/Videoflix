"""Signals for upload app."""
 
import os
import django_rq
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
 
from upload_app.models import FileUpload, Video
from .tasks import convert_to_hls
 
 
def create_video_from_upload(instance):
    """Creates a Video object from a FileUpload instance."""
    return Video.objects.create(
        title=instance.title,
        description=instance.description,
        category=instance.category,
    )
 
 
def enqueue_hls_conversion(video_id, file_path):
    """Enqueues the HLS conversion job in the default queue."""
    queue = django_rq.get_queue('default')
    queue.enqueue(convert_to_hls, video_id, file_path)
 
 
@receiver(post_save, sender=FileUpload)
def handle_file_upload(sender, instance, created, **kwargs):
    """Creates a Video object and starts HLS conversion after a FileUpload is saved."""
    if not created:
        return
    video = create_video_from_upload(instance)
    instance.video = video
    FileUpload.objects.filter(pk=instance.pk).update(video=video)
    enqueue_hls_conversion(video.id, instance.file.path)
 
 
@receiver(post_delete, sender=FileUpload)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Deletes the raw upload file and the linked Video when a FileUpload is deleted."""
    if instance.file and os.path.isfile(instance.file.path):
        os.remove(instance.file.path)
    if instance.video:
        instance.video.delete()
 
 
@receiver(pre_save, sender=FileUpload)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """Deletes old file from filesystem when the FileUpload is updated with a new file."""
    if not instance.pk:
        return
    try:
        old_file = FileUpload.objects.get(pk=instance.pk).file
    except FileUpload.DoesNotExist:
        return
    if old_file and old_file != instance.file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
            