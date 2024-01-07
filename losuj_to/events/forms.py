from django import forms
from django.core.validators import EmailValidator
from events.models import Event


class EventInformationForm(forms.Form):
    event_name = forms.CharField(max_length=100, required=True, label="Event Name")
    # event_location = forms.CharField(max_length=255, required=False, label='Event Location')
    event_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={"type": "date"}),
        label="Date of exchanging gifts",
    )
    draw_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        label="Date of Drawing Names",
    )
    price_limit = forms.IntegerField(required=False, label="Price Limit for the Gift")
    # price_currency = forms.ModelChoiceField(
    #     qyeryset=Event.Currency.choices,
    #     widget=forms.Select(),
    #     label='Price Limit currency'

    # )
    price_currency = forms.ChoiceField(
        choices=Event.Currency.choices,
        widget=forms.Select(),
        label="Price Limit currency",
    )


class EventInformationForm1(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["event_name", "event_date"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["event_name"].label = "Event Name"
        self.fields["date"].label = "Gift echange date"

    widgets = {
        "date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
    }


class BulkUserRegistrationForm(forms.Form):
    participants = forms.CharField(
        max_length=1024, label="User data", required=True, widget=forms.Textarea
    )

    def clean_participants(self):
        print(self.cleaned_data["participants"])
        data = self.cleaned_data["participants"]
        data_export = []
        rows = data.split("\n")
        validator = EmailValidator()
        print(f"printing rows:{rows}")
        print(len(rows))
        for row in rows:
            email = row.split(",")[0].rstrip()
            name = row.split(",")[1].rstrip()
            try:
                validator(email)
                print(f"{email} validated")
                data_export.append([email, name])
            except Exception as e:
                print(e)
                pass
        return data_export
