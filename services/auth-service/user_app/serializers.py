from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
import re




User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=120)
    username = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=["developer", "mentor"])

    # ---------- FIELD LEVEL VALIDATIONS ----------

    def validate_username(self, value):
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise serializers.ValidationError(
                "Username can contain only letters, numbers, and underscores"
            )

        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")

        return value

    def validate_email(self, value):
        value = value.lower()

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")

        return value

    def validate_phone(self, value):
        if not re.match(r"^[6-9]\d{9}$", value):
            raise serializers.ValidationError("Invalid Indian phone number")

        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone number already registered")

        return value

    def validate_password(self, value):
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError(
                "Password must contain an uppercase letter"
            )
        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError(
                "Password must contain a lowercase letter"
            )
        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError("Password must contain a digit")
        if not re.search(r"[!@#$%^&*()_+=\-{}[\]:;\"'<>,.?/]", value):
            raise serializers.ValidationError(
                "Password must contain a special character"
            )

        return value

    def validate_role(self, value):
        return value.upper()

    # ---------- OBJECT LEVEL VALIDATION ----------

    def validate(self, attrs):
        if attrs["username"] == attrs["password"]:
            raise serializers.ValidationError(
                "Username and password cannot be the same"
            )

        return attrs
