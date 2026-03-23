"""Views for content API endpoints."""
 
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
 
from content_app.models import Video
from .serializers import VideoSerializer
 
 
class VideoListView(APIView):
    """Returns a list of all available videos."""
 
    permission_classes = [IsAuthenticated]
 
    def get(self, request):
        """Returns metadata for all videos."""
        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    