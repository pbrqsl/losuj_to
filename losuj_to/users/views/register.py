from typing import Any

from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from django.views.generic.edit import CreateView
from users.forms import BultUserRegistrationForm, CustomUserCreationForm
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
        print(self.object)
        print(form.cleaned_data)
        user = CustomUser.objects.create_user(
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password1"],
        )

        self.send_verification_email(user)
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
