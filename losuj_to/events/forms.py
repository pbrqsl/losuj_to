from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.forms import HiddenInput
from events.models import Event


class EventCreateForm(forms.Form):
    event_name = forms.CharField(
        max_length=100,
        required=True,
        label="Event Name",
        widget=forms.TextInput(attrs={"class": "event_input"}),
    )
    event_location = forms.CharField(
        max_length=255,
        required=False,
        label="Event Location",
        widget=forms.TextInput(
            attrs={
                "class": "event_input",
            }
        ),
    )
    event_date = forms.DateField(
        required=True,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "event_input",
            }
        ),
        label="Date of exchanging gifts",
    )
    draw_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "event_input"}
        ),
        label="Date of Drawing Names",
    )
    price_limit = forms.IntegerField(
        required=False,
        label="Price Limit for the Gift",
        widget=forms.NumberInput(attrs={"class": "event_input"}),
    )

    price_currency = forms.ChoiceField(
        choices=Event.Currency.choices,
        widget=forms.Select(attrs={"class": "event_input"}),
        label="Price Limit currency",
    )

    def clean(self):
        cleaned_data = super().clean()
        event_date = cleaned_data.get("event_date")
        draw_date = cleaned_data.get("draw_date")
        if draw_date and draw_date.date() >= event_date:
            print("Draw date must occur before the event date.")
            self.add_error("draw_date", "Draw date must occur before the event date.")

        date_now = datetime.now().date()
        if event_date < date_now:
            print("Event occurs in the past!")
            self.add_error("event_date", "Event cannot occur in the past!")
        return cleaned_data


class BulkUserRegistrationForm(forms.Form):
    participants = forms.CharField(
        max_length=1024,
        label="User data",
        required=True,
        widget=forms.Textarea,
        show_hidden_initial=True,
    )

    class Meta:
        exclude = ["participants"]

    def clean_participants(self):
        data = self.cleaned_data["participants"]
        data_export = []
        rows = data.split("\n")
        validator = EmailValidator()
        emails = []
        names = []
        for row in rows:
            email = row.split(",")[0].rstrip()
            name = row.split(",")[1].rstrip()

            if email in emails:
                raise ValidationError("Emails cannot repeat.")
            if name in names:
                raise ValidationError("Name value cannot repeat")
            emails.append(email)
            if name != "":
                names.append(name)
            try:
                validator(email)
                print(f"{email} validated")
                data_export.append([email, name])
            except Exception as e:
                print(e)
                pass

        return data_export


class BultUserRegistrationFormOld(forms.Form):
    new_users = forms.CharField(
        max_length=1024, label="User data", required=True, widget=forms.Textarea
    )

    def clean_new_users(self):
        print(self.cleaned_data["new_users"])
        data = self.cleaned_data["new_users"]
        data_export = []
        rows = data.split("\n")
        validator = EmailValidator()
        print(f"printing rows:{rows}")
        print(len(rows))
        for row in rows:
            email = row.split(",")[0]
            try:
                validator(email)
                print(f"{email} validated")
                data_export.append(email)
            except Exception as e:
                print(e)
                pass
        return data_export


class ExcludeParticipantsForm(forms.Form):
    class Meta:
        widgets = {
            "any_field": HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean
        return cleaned_data


class EventConfirmActivationForm(forms.Form):
    pass


class EventConfirmDeactivationForm(forms.Form):
    pass
