from django.contrib.auth.views import (
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import View
from users.forms import CustomPasswordResetForm
from users.mixins import EmailConfirmationMixin
from users.models import CustomUser


class CustomSendEmailConfirmation(SuccessMessageMixin, EmailConfirmationMixin, View):
    success_message = "Email sent!"

    def get(self, request):
        resend_email = request.session.get("resend_email_user") or request.user.email
        user = get_object_or_404(CustomUser, email=resend_email)
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


class CheckIfMailConfirmed(View):
    def get(self, request):
        return redirect("home")
