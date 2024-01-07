from typing import Any

from allauth.account.utils import has_verified_email
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import FormView
from events.forms import BulkUserRegistrationForm, EventInformationForm
from events.models import Event


class EventInformationView(LoginRequiredMixin, FormView):
    form_class = EventInformationForm
    success_url = "event_participants"
    template_name = "event/event_information.html"

    def form_valid(self, form):
        event_data = form.cleaned_data
        # Store event data in session
        form.cleaned_data["draw_date"] = (
            event_data.get("draw_date").strftime("%Y-%m-%dT%H:%M:%S")
            if event_data.get("draw_date")
            else None
        )
        form.cleaned_data["event_date"] = (
            event_data.get("event_date").strftime("%Y-%m-%d")
            if event_data.get("event_date")
            else None
        )
        self.request.session["event_data"] = event_data
        print('print form.cleaned_data["drawing_date"] ')
        print(form.cleaned_data["event_date"])
        # Redirect to the next stage
        messages.add_message(
            self.request,
            messages.INFO,
            "Proper validation",
        )
        print("print(form.cleaned_data['event_date']):")
        print(form.cleaned_data["event_date"])
        authenicated_user = self.request.user
        print(authenicated_user)
        Event.objects.create(
            event_name=form.cleaned_data["event_name"],
            event_date=form.cleaned_data["event_date"],
            owner=authenicated_user,
        )
        return redirect(self.success_url)

    def form_invalid(self, form):
        # Handle form errors
        # return render(self.request, self.template_name, {'form': form})
        return None

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        user = self.request.user

        email = user.email or None

        print(self.request.session.__dict__)

        if has_verified_email(user, email):
            return super().get(request, *args, **kwargs)
        messages.add_message(
            self.request,
            messages.ERROR,
            "This page is available for confirmed users only. \
                <a href='resend_confirmation_email/'>Resend confirmation email</a>",
        )
        return redirect("home")


class EventParticipantsInformationView(FormView, SuccessMessageMixin):
    template_name = "event/participant_information.html"
    form_class = BulkUserRegistrationForm
    success_url = "home"
    success_message = "yup"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = self.form_class
        event_data = self.request.session["event_data"]
        print(self.request.session.__dict__)

        return render(
            request,
            self.template_name,
            context={"form": form, "event_data": event_data},
        )

    def form_valid(self, form):
        participant_data = form.cleaned_data
        print(f"form.cleaned_data: {participant_data}")
        # Store event data in session
        print(form.cleaned_data)
        self.request.session["participant_data"] = participant_data
        print("print self.request.session")
        print(self.request.session["participant_data"])
        print(self.request.session["event_data"])
        # Redirect to the next stage
        messages.add_message(
            self.request,
            messages.INFO,
            "Proper validation",
        )

        return redirect(self.success_url)

    def form_invalid(self, form):
        print("something went wrong")
        print(self.request.session["participant_data"])
        print(self.request.session["event_data"])
        # Handle form errors
        # return render(self.request, self.template_name, {'form': form})
        return redirect(self.success_url)
