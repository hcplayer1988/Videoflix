"""Serializers for upload API endpoints."""
 
from rest_framework import serializers
from upload_app.models import Video
 
 
class VideoSerializer(serializers.ModelSerializer):
    """Serializer for the Video model including thumbnail URL."""
 
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
 
 
class VideoUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading a new video file."""
 
    class Meta:
        model = Video
        fields = ['id', 'file', 'title', 'description', 'category', 'created_at']
        extra_kwargs = {
            'created_at': {'read_only': True},
        }
        
