# # Register your models here.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ["email", "is_active", "is_staff"]
    ordering = ["email"]
    filter_horizontal = ("groups",)


admin.site.register(CustomUser, CustomUserAdmin)
