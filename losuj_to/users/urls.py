from django.urls import path
from users.views import (
    CustomLoginView,
    CustomLogoutView,
    CustomRegisterView,
    HomeView,
    CustomPasswordReset,
    CustomPasswordResetConfirm,
    CustomPasswordResetDone,
    CustomPasswordResetComplete,
)

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    # path("logout/", logout_view, name="logout"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
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
]
