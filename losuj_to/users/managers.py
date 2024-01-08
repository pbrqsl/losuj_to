from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.tokens import default_token_generator


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The email is mandatory")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if not password:
            user.set_unusable_password()
        else:
            user.set_password(password)

        token = default_token_generator.make_token(user)
        user.user_token = token
        user.save()

        return user

    def create_superuser(self, email, password):
        if password is None:
            raise TypeError("Superusers must have a password.")

        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user
