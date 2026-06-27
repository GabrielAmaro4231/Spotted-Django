from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .avatar_service import get_profile_image_for_email
from .models import UserProfileChangeLog

User = get_user_model()

PROFILE_CHANGE_FIELDS = [
    'email',
    'name',
    'handle',
    'profile_image_url',
    'show_handle_on_leaderboard',
]


def get_profile_snapshot(user):
    return {
        field: getattr(user, field)
        for field in PROFILE_CHANGE_FIELDS
    }


def get_profile_changes(user, validated_data):
    changes = {}

    for field in PROFILE_CHANGE_FIELDS:
        if field not in validated_data:
            continue

        old_value = getattr(user, field)
        new_value = validated_data[field]

        if old_value != new_value:
            changes[field] = {
                'old': old_value,
                'new': new_value,
            }

    if 'password' in validated_data:
        changes['password'] = {
            'changed': True,
        }

    return changes


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email',
            'name',
            'handle',
            'profile_image_url',
            'show_handle_on_leaderboard',
            'password',
        ]
        read_only_fields = ['handle', 'profile_image_url']
        extra_kwargs = {
            'name': {'required': True, 'allow_blank': False},
            'show_handle_on_leaderboard': {'required': False},
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already in use')
        return value

    def validate(self, data):
        user = User(email=data.get('email'))

        try:
            validate_password(data['password'], user)
        except DjangoValidationError as error:
            raise serializers.ValidationError({'password': error.messages}) from error

        return data

    def create(self, validated_data):
        validated_data['profile_image_url'] = get_profile_image_for_email(
            validated_data['email']
        )
        user = User.objects.create_user(**validated_data)
        UserProfileChangeLog.objects.create(
            user=user,
            event_type=UserProfileChangeLog.EVENT_CREATED,
            changes=get_profile_snapshot(user),
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'name',
            'handle',
            'profile_image_url',
            'show_handle_on_leaderboard',
        ]
        read_only_fields = ['id', 'handle', 'profile_image_url']


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            username=data['email'],
            password=data['password']
        )

        if not user:
            raise serializers.ValidationError('Invalid credentials')

        if not user.is_active:
            raise serializers.ValidationError('User is inactive')

        token, _ = Token.objects.get_or_create(user=user)

        return {
            'token': token.key
        }


class UpdateUserSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'email',
            'name',
            'profile_image_url',
            'show_handle_on_leaderboard',
            'password',
            'current_password',
        ]
        read_only_fields = ['profile_image_url']
        extra_kwargs = {
            'email': {'required': False},
            'name': {'required': False, 'allow_blank': False},
            'show_handle_on_leaderboard': {'required': False},
        }

    def validate_email(self, value):
        user = self.instance
        if User.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError('Email already in use')
        return value

    def validate_password(self, value):
        try:
            validate_password(value, self.instance)
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.messages) from error

        return value

    def validate(self, data):
        profile_fields = [
            'email',
            'name',
            'show_handle_on_leaderboard',
            'password',
        ]

        if not any(field in data for field in profile_fields):
            raise serializers.ValidationError('At least one field must be updated')

        if data.get('password') and not data.get('current_password'):
            raise serializers.ValidationError({
                'current_password': 'Current password is required to change password'
            })

        if data.get('password') and not self.instance.check_password(data['current_password']):
            raise serializers.ValidationError({
                'current_password': 'Current password is incorrect'
            })

        if data.get('current_password') and not data.get('password'):
            raise serializers.ValidationError({
                'password': 'Password is required when current_password is provided'
            })

        return data

    def update(self, instance, validated_data):
        validated_data.pop('current_password', None)

        if 'email' in validated_data and validated_data['email'] != instance.email:
            validated_data['profile_image_url'] = get_profile_image_for_email(
                validated_data['email']
            )

        changes = get_profile_changes(instance, validated_data)

        if 'email' in validated_data:
            instance.email = validated_data['email']

        if 'name' in validated_data:
            instance.name = validated_data['name']

        if 'profile_image_url' in validated_data:
            instance.profile_image_url = validated_data['profile_image_url']

        if 'show_handle_on_leaderboard' in validated_data:
            instance.show_handle_on_leaderboard = validated_data['show_handle_on_leaderboard']

        if 'password' in validated_data:
            instance.set_password(validated_data['password'])

        instance.save()

        if changes:
            UserProfileChangeLog.objects.create(
                user=instance,
                event_type=UserProfileChangeLog.EVENT_UPDATED,
                changes=changes,
            )

        return instance
