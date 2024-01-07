from typing import Any

from allauth.account.utils import has_verified_email
from allauth.account.views import LoginView as AllAuthLoginView
from allauth.account.views import SignupView as AllAuthSignupView
from allauth.socialaccount.views import SignupView as SocialSignupView
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import (
    LoginView,
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
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView, View
from django.views.generic.edit import CreateView
from users.forms import (
    BultUserRegistrationForm,
    CustomPasswordResetForm,
    CustomUserCreationForm,
)
from users.mixins import EmailConfirmationMixin
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
        if not token:
            return super().get(self, request, *args, **kwargs)
        user = authenticate(request, token=token)
        if user:
            login(request, user)
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


class CustomSendEmailConfirmation(SuccessMessageMixin, EmailConfirmationMixin, View):
    success_message = "Email sent!"

    def get(self, request):
        resend_email = request.session.get("resend_email_user") or request.user.email
        # user = CustomUser.objects.get(email=resend_email)
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
        # token = default_token_generator.make_token(self.object)
        # self.object.user_token = token
        print(self.object)
        print(form.cleaned_data)
        user = CustomUser.objects.create_user(
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password1"],
        )
        user.save()
        # response = super().form_valid(form)

        self.send_verification_email(user)
        # return response
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


# @login_required
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


# test_view = CustomLoginView.as_view()


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
        # return super().dispatch(request, *args, **kwargs)


# class CustomConnectionsView(ConnectionsView):
#     template_name = "users/connections.html"


class CheckIfMailConfirmed(View):
    def get(self, request):
        user = request.user
        print(has_verified_email(user, user.email))
        return redirect("home")


class BulkUserRegistration(FormView):
    form_class = BultUserRegistrationForm
    # template_name = 'users/bulk_registration_confirm.html'

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
                # user.save()
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
