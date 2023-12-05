from django.contrib.auth.views import (
    LoginView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)

from django.contrib.auth import authenticate, login
from django.contrib.auth.tokens import default_token_generator
from users.models import CustomUser
from django.views.generic.edit import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from users.forms import CustomUserCreationForm, CustomPasswordResetForm
from django.views.generic import TemplateView
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect


class CustomLoginView(LoginView):
    template_name = "users/login.html"
    redirect_field_name = "custom_login_view"
    redirect_authenticated_user = False

    class Meta:
        model = CustomUser

    def get(self, request, *args, **kwargs):
        token = request.GET.get("token")
        if not token:
            return super().get(self, request, *args, **kwargs)
        user = authenticate(request, token=token)
        if user:
            login(request, user)
            return redirect(reverse("home"))
        else:
            return redirect(reverse("login"))


class CustomRegisterView(SuccessMessageMixin, CreateView):
    template_name = "users/register.html"
    form_class = CustomUserCreationForm
    success_message = "Account created"
    success_url = reverse_lazy("home")

    class Meta:
        model = CustomUser

    def form_valid(self, form):
        response = super().form_valid(form)
        token = default_token_generator.make_token(self.object)
        self.object.user_token = token
        self.object.save()

        user = authenticate(self.request, token=token)
        if user:
            login(self.request, user)

        return response


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


test_view = CustomLoginView.as_view()
