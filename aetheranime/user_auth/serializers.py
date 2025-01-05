from rest_framework import serializers
from .models import CustomUser
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


class UserRegistrationSerializer(serializers.ModelSerializer):
    date_of_birth = serializers.DateField(
        required=False,
        allow_null=True,
    )
    profile_picture = serializers.ImageField(
        required=False,
        allow_null=True,
    )

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "password",
            "date_of_birth",
            "profile_picture",
        ]
        extra_kwargs = {"password": {"write_only": True}}

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
        fields = ['username', 'email', 'profile_picture', 'date_of_birth', 'tag']

    def update(self, instance, validated_data):
        # Обновление данных пользователя
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.profile_picture = validated_data.get('profile_picture', instance.profile_picture)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        instance.tag = validated_data.get('tag', instance.tag)
        instance.save()
        return instance
