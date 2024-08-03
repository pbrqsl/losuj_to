from typing import Any

from allauth.account.utils import has_verified_email
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView, View
from users.models import CustomUser


class CustomLoginView(LoginView):
    template_name = "users/login.html"
    redirect_field_name = "custom_login_view"
    redirect_authenticated_user = False
    success_message = "You have been successfully logged in!"

    class Meta:
        model = CustomUser

    def get(self, request, *args, **kwargs):
        token = request.GET.get("token")
        next_url = request.GET.get("next")
        if not token:
            return super().get(self, request, *args, **kwargs)
        user = authenticate(request, token=token)
        if user:
            login(request, user)
            if next_url is not None:
                return redirect(next_url)
            return redirect(reverse("home"))
        else:
            return redirect(reverse("login"))

    def post(self, request: HttpRequest, *args: str, **kwargs: Any):
        print(request.user)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form: AuthenticationForm) -> HttpResponse:
        user = form.get_user()
        next = self.request.POST["next"].strip('"') or "home".strip('"')
        self.success_url = reverse(next)
        verified_email = has_verified_email(user, user.email)
        if verified_email:
            print(self.success_url)
            messages.success(self.request, f"Successfully signed in as {user}")
            return super().form_valid(form)
        self.request.session["resend_email_user"] = user.email
        messages.add_message(
            self.request,
            messages.ERROR,
            "User's email has not been verified, cannot login. \
                <a href='resend_confirmation_email/'>Resend confirmation email</a>",
        )
        return redirect("home")

    def get_success_url(self) -> str:
        return self.success_url


class CustomLogoutView(View):
    success_message = "You have been logged out!"

    def get(self, request):
        logout(request)
        return redirect("home")


class ProfileView(TemplateView):
    template_name = "users/profile.html"

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["is_local_user"] = False
        if not user.is_authenticated:
            return context
        context["is_user_verified"] = has_verified_email(user, user.email)
        if not user.user_token:
            return context
        print("aa")
        context["is_local_user"] = True
        return context
