from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta

from user_app.models import EmailVerificationToken
from user_app.email import send_verification_email  # ADD THIS

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=10)

    phone = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r"^\+?[1-9]\d{9,14}$",
                message="Invalid phone number format"
            )
        ]
    )

    class Meta:
        model = User
        fields = (
            "full_name",
            "username",
            "email",
            "phone",
            "password",
            "role",
        )

    # ---- FIELD VALIDATIONS ----

    def validate_email(self, value):
        email = value.lower().strip()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already registered")
        return email

    def validate_username(self, value):
        username = value.lower().strip()
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Username already taken")
        return username

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone number already registered")
        return value

    def validate_role(self, value):
        if value not in ["developer", "mentor"]:
            raise serializers.ValidationError("Invalid role")
        return value

    # ---- CREATE USER + EMAIL TOKEN ----

    def create(self, validated_data):
        password = validated_data.pop("password")

        # 1️⃣ Create user
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.is_email_verified = False
        user.save()

        # 2️⃣ Create email verification token
        token_obj = EmailVerificationToken.objects.create(
            user=user,
            token=get_random_string(48),
            expires_at=timezone.now() + timedelta(minutes=15)
        )

        # 3️⃣ SEND EMAIL (SMTP)
        send_verification_email(user.email, token_obj.token)

        return user
