from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from users.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["email"]


class CustomPasswordResetForm(PasswordResetForm):
    class Meta:
        user_model = CustomUser
