from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from users.managers import CustomUserManager

# Create your models here.


class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    temporary = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    user_token = models.CharField(max_length=255, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    EMAIL_FIELD = "email"

    def __str__(self) -> str:
        return self.email

    @classmethod
    def get_email_field_name(cls):
        print("getting email")
        try:
            print(cls.EMAIL_FIELD)
            return cls.EMAIL_FIELD
        except AttributeError:
            return "email"
