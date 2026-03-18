"""Utility functions for authentication API endpoints."""
 
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
 
User = get_user_model()
 
 
def generate_uid_and_token(user):
    """Generates a uidb64 and activation token for the given user."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uid, token
 
 
def send_activation_email(user, uid, token):
    """Sends an activation email to the given user."""
    activation_link = f"{settings.FRONTEND_URL}/pages/auth/activate.html?uid={uid}&token={token}"
    send_mail(
        subject="Activate your Videoflix account",
        message=f"Please activate your account:\n\n{activation_link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
 
 
def get_user_from_uid(uidb64):
    """Decodes uidb64 and returns the corresponding user or None."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        return User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None
 
 
def is_valid_activation_token(user, token):
    """Checks whether the activation token is valid for the given user."""
    return default_token_generator.check_token(user, token)
 
 
def activate_user(user):
    """Sets the user as active and saves."""
    user.is_active = True
    user.save()
 
 
def set_auth_cookies(response, access, refresh):
    """Sets httpOnly JWT cookies on the response."""
    cookie_settings = {"httponly": True, "secure": True, "samesite": "Lax"}
    response.set_cookie("access_token", access, **cookie_settings)
    if refresh:
        response.set_cookie("refresh_token", refresh, **cookie_settings)
 
 
def delete_auth_cookies(response):
    """Deletes both auth cookies from the response."""
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
 
 
def build_user_response(user):
    """Builds the user data dict for login response."""
    return {
        "detail": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username,
        }
    }

