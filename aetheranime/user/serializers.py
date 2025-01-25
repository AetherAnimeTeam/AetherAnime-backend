from rest_framework import serializers
from .models import CustomUser, Status
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from datetime import timedelta


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Проверяем, активен ли пользователь
        user = attrs.get('user')
        if not user:
            raise serializers.ValidationError('User not found')
        if not user.is_active:
            raise serializers.ValidationError("Аккаунт деактивирован.")

        data = super().validate(attrs)
        data["expires_in"] = api_settings.ACCESS_TOKEN_LIFETIME.total_seconds()
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password", "date_of_birth", "profile_picture"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            date_of_birth=validated_data.get("date_of_birth", None),
            profile_picture=validated_data.get("profile_picture", None),
        )
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "profile_picture", "date_of_birth", "tag"]

    def update(self, instance, validated_data):
        # Обновление данных пользователя
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.profile_picture = validated_data.get(
            "profile_picture", instance.profile_picture
        )
        instance.date_of_birth = validated_data.get(
            "date_of_birth", instance.date_of_birth
        )
        instance.tag = validated_data.get("tag", instance.tag)
        instance.save()
        return instance


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ["anime_id", "status"]

    def validate_status(self, value):
        """
        Проверяем, что статус допустим.
        """
        if value not in dict(Status.STATUS_CHOICES).keys():
            raise serializers.ValidationError("Недопустимый статус.")
        return value
