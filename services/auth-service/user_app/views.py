import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from .serializers import RegisterSerializer
from utils.redis_client import redis_client
from utils.otp import generate_otp
from tasks.email_tasks import send_otp_email
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class RegisterAPIView(APIView):
    """
    Register user (STEP 6 – UPDATED):
    - Validate input
    - Generate OTP + otp_id
    - Store temp data in Redis using otp_id
    - Send OTP via Celery
    - Return otp_id to client
    """

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        email = data["email"]

        # 🔑 Generate OTP session ID
        otp_id = str(uuid.uuid4())
        redis_key = f"otp_reg:{otp_id}"

        otp = generate_otp()

        payload = {
            "email": email,
            "otp": otp,
            "attempts": 0,
            "full_name": data["full_name"],
            "username": data["username"],
            "phone": data["phone"],
            "password": make_password(data["password"]),
            "role": data["role"],  # already uppercased
        }

        # ⏱ Store in Redis (TTL = 5 minutes)
        redis_client.setex(
            redis_key,
            300,  # seconds
            json.dumps(payload)
        )

        # 📧 Send OTP asynchronously
        send_otp_email.delay(email, otp)

        return Response(
            {
                "message": "OTP sent to your email",
                "otp_id": otp_id
            },
            status=status.HTTP_201_CREATED
        )


class VerifyOTPAPIView(APIView):
    """
    Verify OTP (UPDATED):
    - Accepts otp_id + otp
    - Reads temp data from Redis
    - Enforces attempt limits
    - Creates user ONLY on success
    - Deletes Redis key
    """

    MAX_ATTEMPTS = 5

    def post(self, request):
        otp_id = request.data.get("otp_id")
        otp_input = request.data.get("otp")

        if not otp_id or not otp_input:
            return Response(
                {"error": "otp_id and otp are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        redis_key = f"otp_reg:{otp_id}"
        data = redis_client.get(redis_key)

        # ❌ OTP expired or invalid session
        if not data:
            return Response(
                {"error": "OTP expired or invalid"},
                status=status.HTTP_400_BAD_REQUEST
            )

        payload = json.loads(data)

        # 🚫 Too many attempts
        if payload.get("attempts", 0) >= self.MAX_ATTEMPTS:
            redis_client.delete(redis_key)
            return Response(
                {"error": "Too many failed attempts"},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # ❌ Wrong OTP
        if payload["otp"] != otp_input:
            payload["attempts"] = payload.get("attempts", 0) + 1

            # Preserve remaining TTL
            ttl = redis_client.ttl(redis_key)
            redis_client.setex(redis_key, ttl, json.dumps(payload))

            return Response(
                {"error": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ OTP CORRECT — CREATE USER
        user = User.objects.create(
            email=payload["email"],
            username=payload["username"],
            full_name=payload["full_name"],
            phone=payload["phone"],
            password=payload["password"],  # already hashed
            role=payload["role"],
            is_email_verified=True,
            is_active=True,
        )

        # 🧹 Cleanup Redis
        redis_client.delete(redis_key)

        return Response(
            {"message": "Registration successful"},
            status=status.HTTP_201_CREATED
        )


class ResendOTPAPIView(APIView):
    """
    Resend OTP (otp_id-based)
    - Enforces cooldown
    - Regenerates OTP
    - Updates Redis payload
    """

    COOLDOWN_SECONDS = 60
    OTP_TTL_SECONDS = 300  # 5 minutes

    def post(self, request):
        otp_id = request.data.get("otp_id")

        if not otp_id:
            return Response(
                {"error": "otp_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        redis_key = f"otp_reg:{otp_id}"
        cooldown_key = f"otp_resend:{otp_id}"

        # ❌ No active OTP session
        data = redis_client.get(redis_key)
        if not data:
            return Response(
                {"error": "OTP session expired"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ⏳ Cooldown check
        if redis_client.exists(cooldown_key):
            return Response(
                {"error": "Please wait before requesting a new OTP"},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        payload = json.loads(data)

        # 🔄 Generate new OTP
        new_otp = generate_otp()
        payload["otp"] = new_otp
        payload["attempts"] = 0

        # 🔁 Reset OTP TTL
        redis_client.setex(
            redis_key,
            self.OTP_TTL_SECONDS,
            json.dumps(payload)
        )

        # 🧊 Set cooldown
        redis_client.setex(
            cooldown_key,
            self.COOLDOWN_SECONDS,
            "1"
        )

        # 📧 Send OTP
        send_otp_email.delay(payload["email"], new_otp)

        return Response(
            {"message": "OTP resent successfully"},
            status=status.HTTP_200_OK
        )
