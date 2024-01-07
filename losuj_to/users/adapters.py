from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

# from allauth.account.adapter import generate_emailconfirmation_key


class CustomAdapter(DefaultSocialAccountAdapter):
    # def pre_social_login(self, request, sociallogin):
    #     social_user = sociallogin.user
    #     print(social_user.email)
    #     try:
    #         local_user = get_object_or_404(CustomUser, email=social_user)
    #         print(local_user.social_account)
    #         if not local_user.social_account:
    #             print('home')
    #             return redirect('home')
    #     except:
    #         pass
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
        # confiramtion_key = generate_emailconfirmation_key(u)
        # print(confiramtion_key)

        sociallogin.save(request)
        return None
