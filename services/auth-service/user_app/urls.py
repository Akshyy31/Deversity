from django.urls import path
from user_app import views

urlpatterns=[
    path("register/", views.RegisterAPIView.as_view(), name="register"),
    path("verify-otp/", views.VerifyOTPAPIView.as_view(),name="verify-otp"),
     path("resend-otp/", views.ResendOTPAPIView.as_view(), name="resend-otp"),
]