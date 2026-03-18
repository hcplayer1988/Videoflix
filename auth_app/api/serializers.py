"""Serializers for authentication API endpoints."""
 
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
 
User = get_user_model()
 
 
class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration including password confirmation."""
 
    confirmed_password = serializers.CharField(write_only=True)
 
    class Meta:
        model = User
        fields = ['email', 'password', 'confirmed_password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
        }
 
    def validate_confirmed_password(self, value):
        """Validates that password and confirmed_password match."""
        password = self.initial_data.get('password')
        if password and value and password != value:
            raise serializers.ValidationError('Passwords do not match')
        return value
 
    def validate_email(self, value):
        """Validates that the email address is not already registered."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value
 
    def save(self):
        """Creates and saves a new inactive user with a hashed password."""
        email = self.validated_data['email']
        pw = self.validated_data['password']
        account = User(
            email=email,
            username=email,
            is_active=False,
        )
        account.set_password(pw)
        account.save()
        return account
 
 
class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT serializer that authenticates via email instead of username."""
 
    def __init__(self, *args, **kwargs):
        """Replaces the username field with an email field."""
        super().__init__(*args, **kwargs)
        self.fields.pop('username', None)
        self.fields['email'] = serializers.EmailField()
 
    def validate(self, attrs):
        """Looks up the user by email and authenticates using username."""
        email = attrs.get('email')
        try:
            user = User.objects.get(email=email)
            attrs['username'] = user.username
        except User.DoesNotExist:
            raise serializers.ValidationError('No account found with this email.')
        return super().validate(attrs)
