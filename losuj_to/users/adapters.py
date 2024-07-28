from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomAdapter(DefaultSocialAccountAdapter):
    def is_auto_signup_allowed(self, request, sociallogin):
        return False

    def save_user(self, request, sociallogin, form=None):
        """
        Saves a newly signed up social login. In case of auto-signup,
        the signup form is not available.
        """
        u = sociallogin.user
        u.set_unusable_password()
        u.social_account = True

        sociallogin.save(request)
        return None
