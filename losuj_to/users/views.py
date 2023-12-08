from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import (
    LoginView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.contrib.auth import authenticate, login
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from users.models import CustomUser
from django.views.generic.edit import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from users.forms import (
    CustomUserCreationForm,
    CustomPasswordResetForm,
)

from django.views.generic import TemplateView
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.views.generic import View
from allauth.account.views import (
    SignupView as AllAuthSignupView,
    LoginView as AllAuthLoginView,
)
from allauth.socialaccount.views import SignupView as SocialSignupView, ConnectionsView

from django.contrib import messages


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

    def form_valid(self, form: AuthenticationForm) -> HttpResponse:
        user = form.get_user()
        next = self.request.POST["next"].strip('"') or "home".strip('"')
        print(next)
        self.success_url = reverse(next)
        print(self.success_url)
        messages.success(self.request, f"Successfully signed in as {user}")
        print(self.get_success_url())
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return self.success_url


class CustomLogoutView(View):
    success_message = "You have been logged out!"

    def get(self, request):
        logout(request)
        return redirect("home")


def logout_view(request):
    logout(request)
    return redirect("/")


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


class ProfileView(TemplateView):
    template_name = "users/profile.html"


test_view = CustomLoginView.as_view()


class CustomAllauthSignupView(AllAuthSignupView):
    # form_class = CustomAuthSignupForm
    template_name = "users/register.html"


class CustomAllAuthLoginView(AllAuthLoginView):
    # form_class = CustomAuthSignupForm
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
    # def dispatch(self, request, *args, **kwargs):
    #     print('something')
    #     print(request)
    #     return redirect('home')
    #     return super().dispatch(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if not request.method == "POST":
            return super().dispatch(request, *args, **kwargs)
        email = request.POST["email"]
        if not CustomUser.objects.filter(email=email):
            return super().dispatch(request, *args, **kwargs)
        print(CustomUser.objects.filter(email=email))
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
        return super().dispatch(request, *args, **kwargs)


class CustomConnectionsView(ConnectionsView):
    template_name = "users/connections.html"
