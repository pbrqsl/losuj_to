from django.contrib.auth import get_user_model

user_model = get_user_model()


def social_account_added_handler(sender, request, sociallogin, **kwargs):
    pass
