"""Views for upload API endpoints."""
 
import os
from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
 
from upload_app.models import Video
from .serializers import VideoSerializer, VideoUploadSerializer
 
 
def get_video_file_path(movie_id, resolution, filename):
    """Builds the filesystem path to a video file."""
    return os.path.join(
        settings.MEDIA_ROOT, 'videos', str(movie_id), resolution, filename
    )
 
 
def serve_video_file(path, content_type):
    """Returns a FileResponse for the given path or raises Http404."""
    if not os.path.exists(path):
        raise Http404("File not found.")
    return FileResponse(open(path, 'rb'), content_type=content_type)
 
 
class VideoUploadView(APIView):
    """Handles video file uploads."""
 
    permission_classes = [IsAuthenticated]
 
    def post(self, request, format=None):
        """Uploads a video — signal automatically starts HLS conversion."""
        serializer = VideoUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
 
 
class VideoListView(APIView):
    """Returns a list of all available videos."""
 
    permission_classes = [IsAuthenticated]
 
    def get(self, request):
        """Returns metadata for all videos."""
        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
 
 
class VideoPlaylistView(APIView):
    """Returns the HLS master playlist for a specific video and resolution."""
 
    permission_classes = [IsAuthenticated]
 
    def get(self, request, movie_id, resolution):
        """Returns the m3u8 playlist file for the given movie and resolution."""
        if not Video.objects.filter(pk=movie_id).exists():
            raise Http404("Video not found.")
        path = get_video_file_path(movie_id, resolution, 'index.m3u8')
        return serve_video_file(path, 'application/vnd.apple.mpegurl')
 
 
class VideoSegmentView(APIView):
    """Returns a single HLS video segment for a specific video and resolution."""
 
    permission_classes = [IsAuthenticated]
 
    def get(self, request, movie_id, resolution, segment):
        """Returns the .ts segment file for the given movie, resolution and segment name."""
        if not Video.objects.filter(pk=movie_id).exists():
            raise Http404("Video not found.")
        path = get_video_file_path(movie_id, resolution, segment)
        return serve_video_file(path, 'video/MP2T')
