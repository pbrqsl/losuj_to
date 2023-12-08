"""
URL configuration for losuj_to project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from users.views import (
    CustomAllauthSignupView,
    CustomAllAuthLoginView,
    CustomSocialSignupView,
    CustomConnectionsView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("users.urls")),
    path(
        "accounts/social/signup/",
        CustomSocialSignupView.as_view(),
        name="socialaccount_signup",
    ),
    path("accounts/login/", CustomAllAuthLoginView.as_view(), name="account_login"),
    path("accounts/signup/", CustomAllauthSignupView.as_view(), name="account_signup"),
    path(
        "accounts/social/connections/",
        CustomConnectionsView.as_view(),
        name="socialaccount_connections",
    ),
    path("accounts/", include("allauth.urls")),
]
