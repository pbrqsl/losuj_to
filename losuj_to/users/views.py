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
from django.urls import reverse_lazy
from django.http import JsonResponse


class CustomLoginView(LoginView):
    template_name = "users/login.html"
    redirect_field_name = "custom_login_view"

    class Meta:
        model = CustomUser


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


def token_login_view(request):
    token = request.GET.get("token")
    user = authenticate(request, token=token)

    if user:
        login(request, user)
        return JsonResponse({"message": "Success!"})
    else:
        return JsonResponse({"message": "Fail!"})


# class TokenLoginView(View):
#     def get(self, request, *args, **kwargs):
#         token = kwargs.get('token')

#         if token:
#             # Handle login with token
#             # Perform authentication logic here
#             return JsonResponse({'message': 'Login with token successful'})
#         else:
#             # Redirect to the regular login view if no token is provided
#             return JsonResponse({'message': 'Token not provided'})
