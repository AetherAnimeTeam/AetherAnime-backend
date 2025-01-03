from rest_framework import serializers
from .models import CustomUser


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
