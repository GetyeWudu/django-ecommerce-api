from django.contrib.auth.tokens import (
    default_token_generator,
)
from django.core.mail import send_mail
from django.urls import reverse


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