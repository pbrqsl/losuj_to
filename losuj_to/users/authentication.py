from users.models import CustomUser
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class CustomAuthBackend:
    def authenticate(self, request, username=None, password=None):
        try:
            user = CustomUser.objects.get(email=username)
            if user.check_password(password):
                return user

        except CustomUser.DoesNotExist:
            print("user does not exist")
            return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None


class TokenAuthBackend(ModelBackend):
    def authenticate(self, request, token=None, **kwargs):
        UserModel = get_user_model()
        if token:
            try:
                user = UserModel.objects.get(user_token=token)
                return user
            except UserModel.DoesNotExist:
                return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
