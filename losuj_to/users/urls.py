from django.urls import path
from events.views.home import HomeView
from users.views.login import CustomLoginView, CustomLogoutView, ProfileView
from users.views.management import (
    CheckIfMailConfirmed,
    CustomPasswordChangeView,
    CustomPasswordReset,
    CustomPasswordResetComplete,
    CustomPasswordResetConfirm,
    CustomPasswordResetDone,
    CustomSendEmailConfirmation,
)
from users.views.register import CustomRegisterView

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("register/", CustomRegisterView.as_view(), name="register"),
    path("", HomeView.as_view(), name="home"),
    path("reset_password/", CustomPasswordReset.as_view(), name="password_reset"),
    path(
        "reset_password_confirm/<uidb64>/<token>/",
        CustomPasswordResetConfirm.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset_password_done/",
        CustomPasswordResetDone.as_view(),
        name="password_reset_done1",
    ),
    path(
        "reset_password_complete/",
        CustomPasswordResetComplete.as_view(),
        name="password_reset_complete",
    ),
    path(
        "checkemail/",
        CheckIfMailConfirmed.as_view(),
        name="check_email",
    ),
    path(
        "resend_confirmation_email/",
        CustomSendEmailConfirmation.as_view(),
        name="resend_confirmation_email",
    ),
    path(
        "password_change/",
        CustomPasswordChangeView.as_view(),
        name="password_change_view",
    ),
]
