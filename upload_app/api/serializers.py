"""Serializers for upload API endpoints."""
 
from rest_framework import serializers
from upload_app.models import FileUpload, Video
 
 
class FileUploadSerializer(serializers.ModelSerializer):
    """Serializer for the FileUpload model."""
 
    class Meta:
        model = FileUpload
        fields = ['id', 'file', 'title', 'description', 'category', 'uploaded_at']
        extra_kwargs = {
            'uploaded_at': {'read_only': True},
        }
 
 
class VideoSerializer(serializers.ModelSerializer):
    """Serializer for the Video model."""
 
    thumbnail_url = serializers.SerializerMethodField()
 
    class Meta:
        model = Video
        fields = ['id', 'created_at', 'title', 'description', 'thumbnail_url', 'category']
 
    def get_thumbnail_url(self, obj):
        """Returns the absolute URL of the thumbnail."""
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None