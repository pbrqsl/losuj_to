from django.urls import path
from users.views import (
    BulkUserRegistration,
    BulkUserRegistrationInput,
    CheckIfMailConfirmed,
    CustomLoginView,
    CustomLogoutView,
    CustomPasswordChangeView,
    CustomPasswordReset,
    CustomPasswordResetComplete,
    CustomPasswordResetConfirm,
    CustomPasswordResetDone,
    CustomRegisterView,
    CustomSendEmailConfirmation,
    HomeView,
    ProfileView,
)

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    # path("logout/", logout_view, name="logout"),
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
    # path(
    #     "connections/",
    #     CustomConnectionsView.as_view(),
    #     name="link_google_account",
    # ),
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
    path(
        "bulk_registration/",
        BulkUserRegistration.as_view(),
        name="bulk_registration",
    ),
    path(
        "bulk_registration_input/",
        BulkUserRegistrationInput.as_view(),
        name="bulk_registration_input",
    ),
]
