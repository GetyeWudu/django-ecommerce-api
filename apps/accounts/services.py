from django.contrib.auth.tokens import (
    default_token_generator,
)
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings


def send_password_reset_email(user, request):

    token = default_token_generator.make_token(
        user
    )

    uid = user.pk

    reset_url = (
        f"http://localhost:5173/reset-password/"
        f"{uid}/{token}/"
    )

    send_mail(
        subject="Reset your password",
        message=(
            "Click the following link "
            f"to reset your password:\n\n"
            f"{reset_url}"
        ),
        from_email=None,
        recipient_list=[user.email],
    )


def send_verification_email(user):

    token = default_token_generator.make_token(
        user
    )

    verification_url = (
        f"http://localhost:8000/"
        f"api/v1/auth/verify-email/"
        f"{user.pk}/{token}/"
    )

    send_mail(
        subject="Verify your email",
        message=(
            "Welcome to our store!\n\n"
            "Please verify your email "
            "by clicking the link below:\n\n"
            f"{verification_url}"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )    