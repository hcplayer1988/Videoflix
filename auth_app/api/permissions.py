"""Permissions for authentication API endpoints."""
 
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
 
 
class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that reads the access token from cookies
    instead of the Authorization header.
 
    Used as an additional authentication class alongside the default
    JWTAuthentication to support httpOnly cookie-based auth flows.
    """
 
    def authenticate(self, request):
        """
        Extracts the access token from the 'access_token' cookie and
        validates it. Returns a (user, token) tuple on success.
 
        Returns None if the cookie is missing or the token is invalid,
        allowing other authentication backends to take over.
        """
        access_token = request.COOKIES.get('access_token')
 
        if access_token is None:
            return None
 
        try:
            validated_token = self.get_validated_token(access_token)
            return self.get_user(validated_token), validated_token
        except (InvalidToken, TokenError):
            return None
