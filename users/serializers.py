from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.authtoken.models import Token

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {
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
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']


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
        fields = ['email', 'password', 'current_password']
        extra_kwargs = {
            'email': {'required': False}
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
        if not data.get('email') and not data.get('password'):
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

        if 'email' in validated_data:
            instance.email = validated_data['email']

        if 'password' in validated_data:
            instance.set_password(validated_data['password'])

        instance.save()
        return instance
