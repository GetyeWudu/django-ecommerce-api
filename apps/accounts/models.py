from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager

class User(AbstractUser):
  class Role(models.TextChoices):
        CUSTOMER = "CUSTOMER", "Customer"
        STAFF = "STAFF", "Staff"
        MANAGER = "MANAGER", "Manager"
  username= None
  email = models.EmailField(unique=True,db_index=True)
  USERNAME_FIELD = 'email'
  role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
  phone_number = models.CharField(max_length=20, blank=True, null=True)
  email_verified = models.BooleanField(
    default=False
)
  objects = UserManager()
  REQUIRED_FIELDS = []


  def __str__(self):
      return self.email

 
# Create your models here.
