"""Serializers for upload API endpoints."""
 
from rest_framework import serializers
from upload_app.models import FileUpload
 
 
class FileUploadSerializer(serializers.ModelSerializer):
    """Serializer for the FileUpload model."""
 
    class Meta:
        model = FileUpload
        fields = ['id', 'file', 'title', 'description', 'category', 'uploaded_at']
        extra_kwargs = {
            'uploaded_at': {'read_only': True},
        }