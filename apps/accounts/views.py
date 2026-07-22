from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .services import send_verification_email, send_password_reset_email
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer, PasswordChangeSerializer, PasswordResetRequestSerializer, VerifyEmailSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from.models import User
from django.contrib.auth.tokens import (
    default_token_generator,
)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "id": request.user.id,
                "email": request.user.email,
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "phone_number": request.user.phone_number,
                "role": request.user.role,
            }
        )


class RegisterView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = RegisterSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.save()

        send_verification_email(user)

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "email_verified":
                        user.email_verified,
                },
                "tokens": {
                    "access": str(
                        refresh.access_token
                    ),
                    "refresh": str(refresh),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

        except Exception:
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "Successfully logged out."},
            status=status.HTTP_205_RESET_CONTENT,
        )


class PasswordChangeView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        if not user.check_password(serializer.validated_data["current_password"]):
            return Response(
                {"current_password": "Current password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if serializer.validated_data["new_password"] != serializer.validated_data["confirm_new_password"]:
            return Response(
                {"new_password": "New passwords do not match."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = (
            PasswordResetRequestSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.context.get(
            "user"
        )

        if user:
            send_password_reset_email(
                user,
                request,
            )

        return Response(
            {
                "detail":
                "If an account exists, "
                "a reset email has been sent."
            }
        )

class VerifyEmailView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = VerifyEmailSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user_id = serializer.validated_data[
            "user_id"
        ]

        token = serializer.validated_data[
            "token"
        ]

        try:
            user = User.objects.get(
                pk=user_id
            )

        except User.DoesNotExist:

            return Response(
                {
                    "detail":
                    "Invalid verification request."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(
            user,
            token,
        ):

            return Response(
                {
                    "detail":
                    "Invalid or expired token."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.email_verified = True

        user.save(
            update_fields=[
                "email_verified"
            ]
        )

        return Response(
            {
                "detail":
                "Email verified successfully."
            }
        )    
