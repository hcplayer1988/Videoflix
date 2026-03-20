"""Views for authentication API endpoints."""
 
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
 
from .serializers import (
    RegistrationSerializer, EmailTokenObtainPairSerializer, PasswordConfirmSerializer,
)
from .utils import (
    generate_uid_and_token, send_activation_email, send_password_reset_email,
    get_user_from_uid, is_valid_activation_token, activate_user,
    set_auth_cookies, delete_auth_cookies, build_user_response,
)
 
User = get_user_model()
 
 
class RegisterView(APIView):
    """Handles user registration."""
 
    permission_classes = [AllowAny]
 
    def post(self, request):
        """Creates a new inactive user and sends an activation email."""
        serializer = RegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        uid, token = generate_uid_and_token(user)
        send_activation_email(user, uid, token)
        return Response(
            {"user": {"id": user.id, "email": user.email}, "token": token},
            status=status.HTTP_201_CREATED
        )
 
 
class ActivateView(APIView):
    """Handles user account activation via email link."""
 
    permission_classes = [AllowAny]
 
    def get(self, request, uidb64, token):
        """Activates the user account if the token is valid."""
        user = get_user_from_uid(uidb64)
        if user is None or not is_valid_activation_token(user, token):
            return Response(
                {"message": "Activation failed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        activate_user(user)
        return Response(
            {"message": "Account successfully activated."},
            status=status.HTTP_200_OK
        )
 
 
class LoginView(TokenObtainPairView):
    """Handles user login via email and sets JWT tokens as httpOnly cookies."""
 
    permission_classes = [AllowAny]
    serializer_class = EmailTokenObtainPairSerializer
 
    def post(self, request, *args, **kwargs):
        """Authenticates the user by email and sets access and refresh tokens as cookies."""
        response = super().post(request, *args, **kwargs)
        if response.status_code != 200:
            return response
        user = User.objects.get(email=request.data.get("email"))
        set_auth_cookies(response, response.data.get("access"), response.data.get("refresh"))
        response.data = build_user_response(user)
        return response
 
 
class LogoutView(APIView):
    """Handles user logout and invalidates the refresh token."""
 
    permission_classes = [IsAuthenticated]
 
    def post(self, request):
        """Blacklists the refresh token and deletes both auth cookies."""
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token is None:
            return Response({"detail": "Refresh token not found!"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            return Response({"detail": "Token is invalid or already blacklisted!"}, status=status.HTTP_400_BAD_REQUEST)
        response = Response(
            {"detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."},
            status=status.HTTP_200_OK
        )
        delete_auth_cookies(response)
        return response
 
 
class PasswordResetView(APIView):
    """Handles password reset requests."""
 
    permission_classes = [AllowAny]
 
    def post(self, request):
        """Sends a password reset email if the user exists."""
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
            uid, token = generate_uid_and_token(user)
            send_password_reset_email(user, uid, token)
        except User.DoesNotExist:
            pass
        return Response(
            {"detail": "An email has been sent to reset your password."},
            status=status.HTTP_200_OK
        )
 
 
class PasswordConfirmView(APIView):
    """Handles password reset confirmation."""
 
    permission_classes = [AllowAny]
 
    def post(self, request, uidb64, token):
        """Validates the token and sets the new password."""
        user = get_user_from_uid(uidb64)
        if user is None or not is_valid_activation_token(user, token):
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = PasswordConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(
            {"detail": "Your Password has been successfully reset."},
            status=status.HTTP_200_OK
        )
 
 
class CookieTokenRefreshView(TokenRefreshView):
    """Handles access token renewal using the refresh token cookie."""
 
    def post(self, request, *args, **kwargs):
        """Issues a new access token using the refresh token from cookies."""
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token is None:
            return Response({"detail": "Refresh token not found!"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            return Response({"detail": "Refresh token invalid!"}, status=status.HTTP_401_UNAUTHORIZED)
        access_token = serializer.validated_data.get("access")
        set_auth_cookies(response := Response(
            {"detail": "Token refreshed", "access": access_token},
            status=status.HTTP_200_OK
        ), access_token, serializer.validated_data.get("refresh"))
        return response
