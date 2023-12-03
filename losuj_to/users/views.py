from django.contrib.auth.views import (
    LoginView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)

# Create your views here.
from users.models import CustomUser
from django.views.generic.edit import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from users.forms import CustomUserCreationForm, CustomPasswordResetForm
from django.views.generic import TemplateView
from django.urls import reverse_lazy


class CustomLoginView(LoginView):
    template_name = "users/login.html"

    class Meta:
        model = CustomUser


class CustomRegisterView(SuccessMessageMixin, CreateView):
    template_name = "users/register.html"
    form_class = CustomUserCreationForm
    success_message = "Account created"
    success_url = reverse_lazy("home")

    class Meta:
        model = CustomUser


class CustomPasswordReset(PasswordResetView):
    template_name = "users/password_reset.html"
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy("password_reset_done1")
    email_template_name = "users/password_reset_email.html"


class CustomPasswordResetConfirm(PasswordResetConfirmView):
    template_name = "users/password_reset_confirm.html"

    class Meta:
        model = CustomUser


class CustomPasswordResetComplete(PasswordResetCompleteView):
    template_name = "users/password_reset_complete.html"


class CustomPasswordResetDone(PasswordResetDoneView):
    template_name = "users/password_reset_done.html"

    class Meta:
        model = CustomUser


class HomeView(TemplateView):
    template_name = "users/home.html"
