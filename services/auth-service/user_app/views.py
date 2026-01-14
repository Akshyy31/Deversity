from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user_app.serializers import RegisterSerializer
from user_app.models import EmailVerificationToken


class RegisterAPIView(APIView):
    permission_classes = []  # public endpoint
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Registration successful. Please verify your email."},
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailAPIView(APIView):
    permission_classes = []                  # public
    def get(self, request):
        token_value = request.query_params.get("token")
        if not token_value:
            return Response(
                {"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = EmailVerificationToken.objects.select_related("user").get(
                token=token_value
            )
        except EmailVerificationToken.DoesNotExist:
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )
        if not token.is_valid():
            return Response(
                {"error": "Token expired or already used"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = token.user
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])

        token.is_used = True
        token.save(update_fields=["is_used"])

        return Response(
            {"message": "Email verified successfully"}, status=status.HTTP_200_OK
        )
