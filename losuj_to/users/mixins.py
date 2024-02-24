from allauth.account.models import EmailConfirmation, EmailAddress
from django.utils import timezone


class EmailConfirmationMixin:
    def send_verification_email(self, user):
        user_email = user.email
        email_address, created = EmailAddress.objects.get_or_create(
            user=user, email=user_email, verified=False
        )

        emailconfirmation = EmailConfirmation.create(email_address)
        emailconfirmation.sent = timezone.now()
        emailconfirmation.key_expired = False

        emailconfirmation.save()
        emailconfirmation.send()
