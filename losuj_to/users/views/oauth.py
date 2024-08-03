from allauth.account.views import LoginView as AllAuthLoginView
from allauth.account.views import SignupView as AllAuthSignupView
from allauth.socialaccount.views import SignupView as SocialSignupView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from users.models import CustomUser


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
