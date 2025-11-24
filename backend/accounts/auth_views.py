# Real Authentication System for Vatochito
# Supports: Google OAuth, Phone/OTP (SMS), Email verification

from django.contrib.auth import get_user_model
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from django.conf import settings
import random
import string

# Optional imports with fallbacks
try:
    import phonenumbers
    PHONENUMBERS_AVAILABLE = True
except ImportError:
    PHONENUMBERS_AVAILABLE = False
    phonenumbers = None

try:
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False
    id_token = None
    google_requests = None

User = get_user_model()

# ==================== UTILITIES ====================

def generate_otp(length=6):
    """Generate random OTP code"""
    return ''.join(random.choices(string.digits, k=length))

def send_sms_otp(phone_number, otp):
    """Send OTP via Twilio SMS"""
    try:
        from twilio.rest import Client
        
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        from_number = settings.TWILIO_PHONE_NUMBER
        
        client = Client(account_sid, auth_token)
        
        message = client.messages.create(
            body=f'Your Vatochito verification code is: {otp}. Valid for 10 minutes.',
            from_=from_number,
            to=phone_number
        )
        
        return True, message.sid
    except Exception as e:
        print(f"SMS Error: {e}")
        return False, str(e)

def validate_phone_number(phone):
    """Validate and format phone number"""
    if not PHONENUMBERS_AVAILABLE:
        # Basic validation without phonenumbers library
        if phone.startswith('+') and len(phone) > 10:
            return phone, None
        return None, "Phone number must start with + and country code"
    
    try:
        parsed = phonenumbers.parse(phone, None)
        if not phonenumbers.is_valid_number(parsed):
            return None, "Invalid phone number"
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164), None
    except Exception as e:
        return None, str(e)

def get_tokens_for_user(user):
    """Generate JWT tokens for user"""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# ==================== SERIALIZERS ====================

class PhoneOTPRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

class PhoneOTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField(max_length=6)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

class GoogleAuthSerializer(serializers.Serializer):
    token = serializers.CharField()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'phone_number', 'avatar', 'bio', 'status_message', 'is_online']
        read_only_fields = ['id', 'username', 'is_online']

# ==================== VIEWS ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def request_phone_otp(request):
    """
    Send OTP to phone number
    POST /api/auth/phone/request-otp/
    Body: { "phone_number": "+919876543210" }
    """
    serializer = PhoneOTPRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    phone_number = serializer.validated_data['phone_number']
    
    # Validate phone number
    formatted_phone, error = validate_phone_number(phone_number)
    if error:
        return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
    
    # Generate OTP
    otp = generate_otp()
    
    # Store OTP in cache (10 minutes expiry)
    cache_key = f'otp_{formatted_phone}'
    cache.set(cache_key, otp, timeout=600)  # 10 minutes
    
    # Send SMS
    if settings.DEBUG:
        # In development, just return OTP (don't send real SMS)
        return Response({
            'message': 'OTP generated (DEV MODE)',
            'phone_number': formatted_phone,
            'otp': otp,  # Only in DEBUG mode
            'expires_in': 600
        })
    else:
        # Production: Send real SMS
        success, result = send_sms_otp(formatted_phone, otp)
        if success:
            return Response({
                'message': 'OTP sent successfully',
                'phone_number': formatted_phone,
                'expires_in': 600
            })
        else:
            return Response({
                'error': 'Failed to send OTP',
                'details': result
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_phone_otp(request):
    """
    Verify OTP and login/register user
    POST /api/auth/phone/verify-otp/
    Body: { 
        "phone_number": "+919876543210",
        "otp": "123456",
        "first_name": "John",  # Optional for new users
        "last_name": "Doe"     # Optional for new users
    }
    """
    serializer = PhoneOTPVerifySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    phone_number = serializer.validated_data['phone_number']
    otp = serializer.validated_data['otp']
    
    # Validate phone number
    formatted_phone, error = validate_phone_number(phone_number)
    if error:
        return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check OTP
    cache_key = f'otp_{formatted_phone}'
    stored_otp = cache.get(cache_key)
    
    if not stored_otp:
        return Response({
            'error': 'OTP expired or not found'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if stored_otp != otp:
        return Response({
            'error': 'Invalid OTP'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # OTP is valid - delete it
    cache.delete(cache_key)
    
    # Get or create user
    user, created = User.objects.get_or_create(
        phone_number=formatted_phone,
        defaults={
            'username': formatted_phone.replace('+', '').replace('-', ''),
            'first_name': serializer.validated_data.get('first_name', ''),
            'last_name': serializer.validated_data.get('last_name', ''),
        }
    )
    
    # Update online status
    user.is_online = True
    user.save(update_fields=['is_online'])
    
    # Generate tokens
    tokens = get_tokens_for_user(user)
    
    return Response({
        'message': 'Login successful' if not created else 'Account created successfully',
        'user': UserSerializer(user).data,
        'tokens': tokens,
        'is_new_user': created
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def google_auth(request):
    """
    Authenticate with Google OAuth
    POST /api/auth/google/
    Body: { "token": "google_id_token" }
    """
    serializer = GoogleAuthSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    token = serializer.validated_data['token']
    
    try:
        # Verify Google token
        idinfo = id_token.verify_oauth2_token(
            token, 
            google_requests.Request(), 
            settings.GOOGLE_OAUTH_CLIENT_ID
        )
        
        # Get user info from Google
        email = idinfo['email']
        google_id = idinfo['sub']
        first_name = idinfo.get('given_name', '')
        last_name = idinfo.get('family_name', '')
        picture = idinfo.get('picture', '')
        email_verified = idinfo.get('email_verified', False)
        
        if not email_verified:
            return Response({
                'error': 'Email not verified with Google'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0] + '_' + google_id[:6],
                'first_name': first_name,
                'last_name': last_name,
            }
        )
        
        # Update online status
        user.is_online = True
        user.save(update_fields=['is_online'])
        
        # Generate tokens
        tokens = get_tokens_for_user(user)
        
        return Response({
            'message': 'Login successful' if not created else 'Account created successfully',
            'user': UserSerializer(user).data,
            'tokens': tokens,
            'is_new_user': created
        })
        
    except ValueError as e:
        return Response({
            'error': 'Invalid Google token',
            'details': str(e)
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def logout(request):
    """
    Logout user
    POST /api/auth/logout/
    """
    user = request.user
    user.is_online = False
    user.save(update_fields=['is_online'])
    
    return Response({'message': 'Logged out successfully'})
