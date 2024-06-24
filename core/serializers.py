import magic

from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.hashers import make_password
from django.utils.http import  urlsafe_base64_decode
from django.utils.encoding import force_str

from rest_framework import  serializers

from botocore.exceptions import NoCredentialsError

from .models import Profile
from .clients import s3_client, R2_BUCKET_NAME

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)
        exclude = kwargs.pop('exclude', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        if exclude is not None:
            # Drop fields specified in 'exclude' argument
            for field_name in exclude:
                self.fields.pop(field_name, None)

class SignupSerializer(serializers.ModelSerializer):
    """ Signup New User Serializer Class """
    class Meta :
        model = User
        fields = ['username','email','password']


    def validate_password(self, value: str) -> str:
        return make_password(value)

class ProfileSerializer(DynamicFieldsModelSerializer):
    """ Profile Serializer """

    profile_picture = serializers.ImageField(write_only=True, required=False)
    profile_picture_url = serializers.URLField(source='profile_picture', read_only=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

    class Meta:
        model = Profile
        fields = ('bio', 'profile_picture', 'profile_picture_url', 'first_name', 'last_name')
        extra_kwargs = {
            'user': {'write_only': True}
        }


    def to_representation(self, instance):
        """
        Modify the output representation to conditionally include 'first_name' and 'last_name'
        from the related User instance, based on requested fields.
        """
        representation = super(ProfileSerializer, self).to_representation(instance)

        # Get requested fields from context
        requested_fields = self.context.get('requested_fields', [])

        if 'first_name' in requested_fields:
            representation['first_name'] = instance.user.first_name
        if 'last_name' in requested_fields:
            representation['last_name'] = instance.user.last_name

        return representation

    def validate_profile_picture(self, value):
        """
        Check that the uploaded file is an image.
        """
        SUPPORTED_TYPES = ['jpg', 'jpeg', 'png', 'svg']
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(value.read())
        value.seek(0)
        if mime_type.split('/')[1] not in SUPPORTED_TYPES:
            raise serializers.ValidationError(f"Only image files witn extensions {SUPPORTED_TYPES} allowed.")
        return value
    
    def update(self, profile, validated_data):
        first_name = validated_data.pop('first_name', profile.user.first_name)
        last_name = validated_data.pop('last_name', profile.user.last_name)
        profile_picture = validated_data.pop('profile_picture', None)

        profie_pic_name = f"{first_name.lower()}_{last_name.lower()}_profile"
        if profile_picture:
            try:
                mime = magic.Magic(mime=True)
                mime_type = mime.from_buffer(profile_picture.read())
                profile_picture.seek(0)
                image_name = f"profile/{profie_pic_name}.{mime_type.split('/')[1]}"
                s3_client.upload_fileobj(
                    profile_picture,
                    R2_BUCKET_NAME,
                    image_name,
                    ExtraArgs={'ContentType': f'{mime_type}'}
                )
                file_url = s3_client.generate_presigned_url('get_object',
                    Params={'Bucket': R2_BUCKET_NAME, 'Key': f"{image_name}"},
                    ExpiresIn=604799 #week expiry
                )
                validated_data['profile_picture'] = file_url
            except NoCredentialsError:
                raise serializers.ValidationError("Credentials not available")
            except Exception as e:
                raise serializers.ValidationError(f"Error uploading profile image: {str(e)}")

        if first_name is not None or last_name is not None:
            user = profile.user
            if first_name is not None:
                user.first_name = first_name
            if last_name is not None:
                user.last_name = last_name
            user.save()

        return super(ProfileSerializer, self).update(profile, validated_data)

class UserSerializer(DynamicFieldsModelSerializer):
    profile = serializers.SerializerMethodField()
    fullname = serializers.SerializerMethodField()
    class Meta :
        model = User
        fields = '__all__'


    def get_profile(self, obj):
        if 'profile' not in self.context.get('requested_fields'):
            return None

        profile_fields = self.context.get('profile_fields')

        serializer = ProfileSerializer(obj.profile, context=self.context, fields=profile_fields)
        return serializer.data

    def get_fullname(self, obj):
        return f"{obj.first_name}{obj.last_name}"

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    uidb64 = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, attrs):
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uidb64']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError('Invalid token or user ID.')

        if not PasswordResetTokenGenerator().check_token(user, attrs['token']):
            raise serializers.ValidationError('Invalid token or user ID.')

        return attrs

    def save(self):
        uid = force_str(urlsafe_base64_decode(self.validated_data['uidb64']))
        user = User.objects.get(pk=uid)
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user