import pytest

from apps.accounts.models import User


@pytest.mark.django_db
def test_create_user():

    user = User.objects.create_user(
        email="test@example.com",
        password="StrongPassword123",
    )

    assert user.email == "test@example.com"

    assert user.check_password(
        "StrongPassword123"
    )

    assert user.role == User.Role.CUSTOMER

    assert user.is_staff is False

    assert user.is_superuser is False

@pytest.mark.django_db
def test_create_superuser():

    user = User.objects.create_superuser(
        email="admin@example.com",
        password="StrongPassword123",
    )

    assert user.is_staff is True

    assert user.is_superuser is True

    assert user.role == User.Role.MANAGER    