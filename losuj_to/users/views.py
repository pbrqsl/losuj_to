from typing import Any

from allauth.account.utils import has_verified_email
from allauth.account.views import LoginView as AllAuthLoginView
from allauth.account.views import SignupView as AllAuthSignupView
from allauth.socialaccount.views import SignupView as SocialSignupView
from django.contrib import messages
from django.contrib.auth.views import (
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView, View
from django.views.generic.edit import CreateView
from users.forms import (
    BultUserRegistrationForm,
    CustomPasswordResetForm,
    CustomUserCreationForm,
)
from users.mixins import EmailConfirmationMixin
from users.models import CustomUser


class CustomSendEmailConfirmation(SuccessMessageMixin, EmailConfirmationMixin, View):
    success_message = "Email sent!"

    def get(self, request):
        resend_email = request.session.get("resend_email_user") or request.user.email
        user = get_object_or_404(CustomUser, email=resend_email)
        self.send_verification_email(user)
        return redirect("home")


class CustomRegisterView(SuccessMessageMixin, EmailConfirmationMixin, CreateView):
    template_name = "users/register.html"
    form_class = CustomUserCreationForm
    success_message = "Account created. Please check your email for verification link."
    success_url = reverse_lazy("home")

    class Meta:
        model = CustomUser

    def form_valid(self, form):
        print(self.object)
        print(form.cleaned_data)
        user = CustomUser.objects.create_user(
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password1"],
        )

        self.send_verification_email(user)
        return redirect("home")


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


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "users/password_change.html"


class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = "users/password_change_done.html"


class HomeView(TemplateView):
    template_name = "users/home.html"


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


class CustomAllauthSignupView(AllAuthSignupView):
    template_name = "users/register.html"


class CustomAllAuthLoginView(AllAuthLoginView):
    template_name = "users/login.html"

    def form_valid(self, form):
        print("this is request")
        print(self.request)
        print("this is postrequest")
        return super().form_valid(form)

    def form_invalid(self, form) -> HttpResponse:
        print("this is request")
        print(self.request)
        print("this is postrequest")
        return super().form_invalid(form)


class CustomSocialSignupView(SuccessMessageMixin, SocialSignupView):
    template_name = "users/social_signup.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.method == "POST":
            return super().dispatch(request, *args, **kwargs)
        email = request.POST["email"]
        if not CustomUser.objects.filter(email=email):
            return super().dispatch(request, *args, **kwargs)

        messages.add_message(
            request,
            messages.ERROR,
            f"An account with email {email} already exists in the local account \
                repository.",
        )
        messages.add_message(
            request,
            messages.ERROR,
            "Please login with local account credentials and use \
            <Link with Social App!> option in profile view \
            to configure login with google.",
        )
        return redirect("home")


class CheckIfMailConfirmed(View):
    def get(self, request):
        user = request.user
        print(has_verified_email(user, user.email))
        return redirect("home")


class BulkUserRegistration(FormView):
    form_class = BultUserRegistrationForm

    def form_valid(self, form: Any) -> HttpResponse:
        print("form_valid starts")
        new_users = []
        print(form.cleaned_data["new_users"])
        print(type(form.cleaned_data["new_users"]))
        for row in form.cleaned_data["new_users"]:
            email = row.split(",")[0]
            print(f"row: {email}")
            if CustomUser.objects.filter(email=email):
                print("user exists")
                continue
            try:
                user = CustomUser.objects.create_user(email=email, password=None)
                new_users.append(user)
                print("user created")
            except ValidationError:
                pass
        print(new_users)

        return render(
            self.request,
            "users/bulk_registration_confirm.html",
            {"new_users": new_users},
        )


class BulkUserRegistrationInput(TemplateView):
    template_name = "users/bulk_registration.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = BultUserRegistrationForm()

        return render(request, self.template_name, context={"form": form})
