"""RQ background tasks for video processing."""
 
import os
import subprocess
from django.conf import settings
 
 
RESOLUTIONS = {
    '480p': '854x480',
    '720p': '1280x720',
    '1080p': '1920x1080',
}
 
 
def get_output_dir(video_id, resolution):
    """Returns the output directory path for a given video and resolution."""
    return os.path.join(settings.MEDIA_ROOT, 'videos', str(video_id), resolution)
 
 
def build_ffmpeg_command(input_path, output_dir, resolution):
    """Builds the ffmpeg command for HLS conversion."""
    scale = RESOLUTIONS[resolution]
    playlist = os.path.join(output_dir, 'index.m3u8')
    segment = os.path.join(output_dir, '%03d.ts')
    return [
        'ffmpeg', '-i', input_path,
        '-vf', f'scale={scale}',
        '-c:v', 'libx264', '-c:a', 'aac',
        '-hls_time', '10',
        '-hls_playlist_type', 'vod',
        '-hls_segment_filename', segment,
        playlist,
    ]
 
 
def generate_thumbnail(video_id, input_path):
    """Generates a thumbnail from the video and saves the path to the Video object."""
    from upload_app.models import Video
    thumbnail_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
    os.makedirs(thumbnail_dir, exist_ok=True)
    thumbnail_filename = f'{video_id}.jpg'
    thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)
    command = [
        'ffmpeg', '-i', input_path,
        '-ss', '00:00:05',
        '-vframes', '1',
        '-q:v', '2',
        thumbnail_path,
    ]
    subprocess.run(command, check=True)
    video = Video.objects.get(pk=video_id)
    video.thumbnail = f'thumbnails/{thumbnail_filename}'
    video.save()
 
 
def convert_to_hls(video_id, input_path):
    """Converts a video to HLS format in multiple resolutions and generates a thumbnail."""
    generate_thumbnail(video_id, input_path)
    for resolution in RESOLUTIONS:
        output_dir = get_output_dir(video_id, resolution)
        os.makedirs(output_dir, exist_ok=True)
        command = build_ffmpeg_command(input_path, output_dir, resolution)
        subprocess.run(command, check=True)
        
        