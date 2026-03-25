"""App configuration for upload app."""
 
from django.apps import AppConfig
 
 
class UploadAppConfig(AppConfig):
    """Configuration for the upload app."""
 
    name = 'upload_app'
 
    def ready(self):
        """Registers signal handlers when the app is ready."""
        import upload_app.signals
