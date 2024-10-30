from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from users.forms import CustomUserCreationForm
from users.mixins import EmailConfirmationMixin
from users.models import CustomUser


class CustomRegisterView(SuccessMessageMixin, EmailConfirmationMixin, CreateView):
    template_name = "users/register.html"
    form_class = CustomUserCreationForm
    success_message = "Account created. Please check your email for verification link."
    success_url = reverse_lazy("home")

    class Meta:
        model = CustomUser

    def form_valid(self, form):
        user = CustomUser.objects.create_user(
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password1"],
        )

        self.send_verification_email(user)
        return redirect("home")
