from django.core.mail import send_mail
from django.contrib.auth import logout 
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from rest_framework import status, permissions, views
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from . import serializers
from .responses import DefaultResponse
from .models import Profile
from .helpers import send_password_reset_email


class RegesterationView(GenericAPIView):
    """A simple APIView

    This class register new users

    Methods:
        post: To get the user data and create a new user with it
    """
    serializer_class = serializers.SignupSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        """Get user data from API and create new user

        Args:
            username: The new user username.
            email: The new user email
            password: The new user password.

        Returns:
            status_code: 200.
        """
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if User.objects.filter(email=email).exists() or User.objects.filter(username=username).exists() :
            return Response({
                "error": "A user with this credentials already exists."
            }, status=status.HTTP_400_BAD_REQUEST)

        new_user = User(email=email, username=username, is_active=False)
        new_user.set_password(password)
        new_user.save()

        return DefaultResponse(
            message="User account has been created successfully",
            status=status.HTTP_200_OK,
            status_code=200
        )

class ProfileAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, *args, **kwargs):
        try:
            profile = Profile.objects.get(user=request.user)
        except Exception as _:
            return DefaultResponse(
            message="You have a problem with your profile please contact support",
            status = status.HTTP_400_BAD_REQUEST,
            status_code = 400
        )

        profile_data = serializers.ProfileSerializer(
            profile,
            context={
                'requested_fields':
                    ['first_name', 'last_name']
                },
            exclude=['user'])
        return DefaultResponse(
            message="Profile data retrieved successfully",
            data = {
                'profile':profile_data.data,
                'username':request.user.username
            },
            status = status.HTTP_200_OK,
            status_code = 200
        )


    @swagger_auto_schema(
        operation_description="Update Profile Data",
        manual_parameters=[
            openapi.Parameter('profile_picture', openapi.IN_FORM, description="Profile image file", type=openapi.TYPE_FILE),
            openapi.Parameter('first_name', openapi.IN_FORM, description="First name of the user", type=openapi.TYPE_STRING),
            openapi.Parameter('last_name', openapi.IN_FORM, description="Last name of the user", type=openapi.TYPE_STRING),
            openapi.Parameter('bio', openapi.IN_FORM, description="Bio of the user", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(
                description="Profile data saved successfully",
                examples={
                    "application/json": {
                        "message": "Profile data saved successfully",
                        "data": {
                            "first_name": "John",
                            "last_name": "Doe",
                            "bio": "Software developer",
                            "profile_picture": "http://example.com/media/profile_images/your_image.jpg"
                        },
                        "status_code": 200
                    }
                }
            ),
            400: "Error saving profile data"
        }
    )

    def post(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        profile = Profile.objects.get(user=user)
        profile_serializer = serializers.ProfileSerializer(
            profile,
            data=data,
            partial=True,
            context={
            'requested_fields':
                ['first_name', 'last_name']
            }
            )
        user_serializer = serializers.UserSerializer(user, data=data, partial=True)

        # Validate and save if valid
        if profile_serializer.is_valid() and user_serializer.is_valid():
            profile_serializer.save()
            user_serializer.save()

            return DefaultResponse(
                message= "Profile data saved successfully",
                data =profile_serializer.data,
                status=status.HTTP_200_OK,
                status_code = 200
            )
        else:
            return DefaultResponse(
                message = "Error saving profile data",
                data = profile_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
                status_code = 400
            )

class CustomLogoutView(views.APIView):
    """
    This is custom Logout view to instant logout user from Django
    and Blacklist Refresh Token
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logout(request)
        
        refresh_token = request.data.get("refresh", None)
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        

         # Clear session data
        request.session.flush()

        # Remove authentication cookies
        response = Response(status=status.HTTP_205_RESET_CONTENT)
        response.delete_cookie('sessionid')
        response.delete_cookie('csrftoken')

        return DefaultResponse(status=status.HTTP_205_RESET_CONTENT)

class PasswordResetView(GenericAPIView):
    serializer_class = serializers.PasswordResetSerializer
    permission_classes = [permissions.AllowAny] 

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=serializer.validated_data['email'])
        token = PasswordResetTokenGenerator().make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        send_password_reset_email(user, uidb64, token)

        return DefaultResponse(
            message="Password reset e-mail has been sent.",
            status=status.HTTP_200_OK,
            status_code=200
        )

class PasswordResetConfirmView(GenericAPIView):
    serializer_class = serializers.PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny] 

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return DefaultResponse(
            message="Password has been reset successfully.",
            status=status.HTTP_200_OK,
            status_code=200
        )