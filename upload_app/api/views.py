"""Views for upload API endpoints."""
 
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
 
from .serializers import FileUploadSerializer
 
 
class FileUploadView(APIView):
    """Handles video file uploads."""
 
    permission_classes = [IsAuthenticated]
 
    def post(self, request, format=None):
        """Uploads a file — signal automatically creates Video and starts HLS conversion."""
        serializer = FileUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)