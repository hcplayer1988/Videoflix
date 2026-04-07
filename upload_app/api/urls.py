"""URL configuration for upload API endpoints."""
 
from django.urls import path
from .views import VideoUploadView, VideoListView, VideoPlaylistView, VideoSegmentView
 
urlpatterns = [
    path('upload/', VideoUploadView.as_view(), name='video-upload'),
    path('video/', VideoListView.as_view(), name='video-list'),
    path('video/<int:movie_id>/<str:resolution>/index.m3u8', VideoPlaylistView.as_view(), name='video-playlist'),
    path('video/<int:movie_id>/<str:resolution>/<str:segment>/', VideoSegmentView.as_view(), name='video-segment'),
]
