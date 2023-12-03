from django.urls import path
from users.views import (
    CustomLoginView,
    CustomRegisterView,
    HomeView,
    CustomPasswordReset,
    CustomPasswordResetConfirm,
    CustomPasswordResetDone,
    CustomPasswordResetComplete,
    token_login_view,
)

urlpatterns = [
    # path("admin/", admin.site.urls),
    path("secret_login/", token_login_view, name="token_login"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("register/", CustomRegisterView.as_view(), name="register"),
    path("home/", HomeView.as_view(), name="home"),
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
