"""Views for authentication API endpoints."""
 
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
 
from .serializers import RegistrationSerializer
 
User = get_user_model()
 
 
class RegisterView(APIView):
    """Handles user registration."""
 
    permission_classes = [AllowAny]
 
    def post(self, request):
        """
        Creates a new inactive user account and sends an activation email.
 
        Returns 201 with user data and activation token on success.
        Returns 400 if the provided data is invalid
        (e.g. passwords do not match or email already exists).
        """
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
 
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
 
            activation_link = f"{settings.FRONTEND_URL}/activate/{uid}/{token}/"
 
            send_mail(
                subject="Activate your Videoflix account",
                message=f"Please activate your account by clicking the link below:\n\n{activation_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
 
            return Response(
                {
                    "user": {
                        "id": user.id,
                        "email": user.email,
                    },
                    "token": token,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class LoginView(TokenObtainPairView):
    """Handles user login and sets JWT tokens as httpOnly cookies."""
 
    permission_classes = [AllowAny]
    serializer_class = TokenObtainPairSerializer
 
    def post(self, request, *args, **kwargs):
        """
        Authenticates the user and sets access and refresh tokens as
        httpOnly cookies. Returns user data on success.
 
        Returns 200 with user info on success, 401 for invalid credentials,
        400 if required fields are missing.
        """
        response = super().post(request, *args, **kwargs)
 
        if response.status_code == 200:
            access = response.data.get("access")
            refresh = response.data.get("refresh")
 
            user = User.objects.get(username=request.data.get("username"))
 
            response.set_cookie(
                key="access_token",
                value=access,
                httponly=True,
                secure=True,
                samesite="Lax"
            )
            response.set_cookie(
                key="refresh_token",
                value=refresh,
                httponly=True,
                secure=True,
                samesite="Lax"
            )
 
            response.data = {
                "detail": "Login successfully!",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                }
            }
 
        return response
 
 
class LogoutView(APIView):
    """Handles user logout and invalidates the refresh token."""
 
    permission_classes = [IsAuthenticated]
 
    def post(self, request):
        """
        Blacklists the refresh token and deletes both auth cookies.
 
        Returns 200 on success, 401 if the refresh token is missing
        or already invalid.
        """
        refresh_token = request.COOKIES.get("refresh_token")
 
        if refresh_token is None:
            return Response(
                {"detail": "Refresh token not found!"},
                status=status.HTTP_401_UNAUTHORIZED
            )
 
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {"detail": "Token is invalid or already blacklisted!"},
                status=status.HTTP_401_UNAUTHORIZED
            )
 
        response = Response(
            {"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."},
            status=status.HTTP_200_OK
        )
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
 
        return response
 
 
class CookieTokenRefreshView(TokenRefreshView):
    """Handles access token renewal using the refresh token cookie."""
 
    def post(self, request, *args, **kwargs):
        """
        Reads the refresh token from cookies and issues a new access token.
 
        If token rotation is enabled, also sets a new refresh token cookie.
        Returns 200 on success, 401 if the refresh token is missing or invalid.
        """
        refresh_token = request.COOKIES.get("refresh_token")
 
        if refresh_token is None:
            return Response(
                {"detail": "Refresh token not found!"},
                status=status.HTTP_401_UNAUTHORIZED
            )
 
        serializer = self.get_serializer(data={"refresh": refresh_token})
 
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            return Response(
                {"detail": "Refresh token invalid!"},
                status=status.HTTP_401_UNAUTHORIZED
            )
 
        access_token = serializer.validated_data.get("access")
        new_refresh_token = serializer.validated_data.get("refresh")
 
        response = Response(
            {"detail": "Token refreshed"},
            status=status.HTTP_200_OK
        )
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Lax"
        )
        if new_refresh_token:
            response.set_cookie(
                key="refresh_token",
                value=new_refresh_token,
                httponly=True,
                secure=True,
                samesite="Lax"
            )
 
        return response
