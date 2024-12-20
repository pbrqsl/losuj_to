from typing import Any

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    PasswordResetForm,
    UserCreationForm,
    _unicode_ci_compare,
)
from django.core.validators import EmailValidator
from users.models import CustomUser

UserModel = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["email"]


class CustomPasswordResetForm(PasswordResetForm):
    class Meta:
        user_model = CustomUser

    def get_users2(self, email):
        """Given an email, return matching user(s) who should receive a reset.

        This allows subclasses to more easily customize the default policies
        that prevent inactive users and users with unusable passwords from
        resetting their password.
        """
        email_field_name = UserModel.get_email_field_name()
        active_users = UserModel._default_manager.filter(
            **{
                "%s__iexact" % email_field_name: email,
                "is_active": True,
            }
        )
        return (
            u
            for u in active_users
            if u.has_usable_password()
            and _unicode_ci_compare(email, getattr(u, email_field_name))
        )

    def get_users(self, email):
        email_field_name = UserModel.get_email_field_name()
        active_users = UserModel._default_manager.filter(
            **{
                "%s__iexact" % email_field_name: email,
                "is_active": True,
            }
        )

        return (
            u
            for u in active_users
            if _unicode_ci_compare(email, getattr(u, email_field_name))
        )

    def send_mail(
        self,
        subject_template_name: str,
        email_template_name: str,
        context: dict[str, Any],
        from_email: str | None,
        to_email: str,
        html_email_template_name: str | None = ...,
    ) -> None:
        return super().send_mail(
            subject_template_name,
            email_template_name,
            context,
            from_email,
            to_email,
            html_email_template_name,
        )


class BultUserRegistrationForm(forms.Form):
    new_users = forms.CharField(
        max_length=1024, label="User data", required=True, widget=forms.Textarea
    )

    def clean_new_users(self):
        data = self.cleaned_data["new_users"]
        data_export = []
        rows = data.split("\n")
        validator = EmailValidator()

        for row in rows:
            email = row.split(",")[0]
            try:
                validator(email)

                data_export.append(email)
            except Exception:
                pass
        return data_export
