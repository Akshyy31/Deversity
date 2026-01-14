from django.urls import path
from user_app import views

urlpatterns=[
    path("register/", views.RegisterAPIView.as_view(), name="register"),
    path("verify-email/", views.VerifyEmailAPIView.as_view()),
]