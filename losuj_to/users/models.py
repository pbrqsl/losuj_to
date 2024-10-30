from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from users.managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    temporary = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    user_token = models.CharField(max_length=255, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    social_account = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"

    def __str__(self) -> str:
        return self.email

    @classmethod
    def get_email_field_name(cls):
        try:
            return cls.EMAIL_FIELD
        except AttributeError:
            return "email"
