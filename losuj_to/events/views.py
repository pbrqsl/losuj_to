import json
from typing import Any

from allauth.account.utils import has_verified_email
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import FormView
from events.forms import (
    BulkUserRegistrationForm,
    EventInformationForm,
    ExcludeParticipantsForm,
)
from events.models import Event, Exclusion, Participant
from users.models import CustomUser


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
        messages.add_message(
            self.request,
            messages.INFO,
            "Proper validation",
        )
        authenicated_user = self.request.user
        event = Event.objects.create(
            event_name=form.cleaned_data["event_name"],
            event_date=form.cleaned_data["event_date"],
            owner=authenicated_user,
        )

        form.cleaned_data["event_id"] = event.id
        return redirect(self.success_url)

    def form_invalid(self, form):
        return render(
            self.request,
            self.template_name,
            context={"form": form},
        )

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        user = self.request.user

        email = user.email or None

        # print(self.request.session.__dict__)

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
    success_url = "event_excludes"
    success_message = "yup"
    num_rows = 2

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = self.form_class
        event_data = self.request.session["event_data"]
        print(self.request.session.__dict__)

        return render(
            request,
            self.template_name,
            context={
                "form": form,
                "event_data": event_data,
                "rows_range": range(self.num_rows),
            },
        )

    def form_valid(self, form):
        event = Event.objects.get(
            id=self.request.session.get("event_data").get("event_id")
        )

        parcipants_data = []
        participants = form.cleaned_data["participants"]
        for participant in participants:
            email = participant[0]
            name = participant[1]
            if name == "":
                name = participant[0]
            try:
                user = CustomUser.objects.get(email=email)
            except ObjectDoesNotExist:
                print("exception")
                user = CustomUser.objects.create_user(email=email, password=None)

            participant, created = Participant.objects.get_or_create(
                user=user, event=event, name=name
            )
            parcipants_data.append([email, name])

        self.request.session["participant_data"] = parcipants_data
        return redirect(self.success_url)

    def form_invalid(self, form):
        event_data = self.request.session["event_data"]
        # print(f'form.cleaned_data: {form.data['participants']}')
        raw_participants = form.data["participants"].split("\n")
        participants = []
        for participant in raw_participants:
            print(participant)
            email = participant.split(",")[0].rstrip()
            name = participant.split(",")[1].rstrip()
            participants.append([email, name])

        print(participants)
        # print(self.request.session["participant_data"])
        # print(self.request.session["event_data"])
        # return redirect(self.success_url)
        return render(
            self.request,
            self.template_name,
            context={
                "form": form,
                "event_data": event_data,
                "participants": participants,
            },
        )


class EventExcludesInformation(FormView, SuccessMessageMixin):
    template_name = "event/excludes_information.html"
    form_class = ExcludeParticipantsForm
    success_url = "home"
    success_message = "yup"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = self.form_class
        event_data = self.request.session["event_data"]
        participants = self.request.session["participant_data"]

        print(self.request.session.__dict__)

        return render(
            request,
            self.template_name,
            context={
                "form": form,
                "event_data": event_data,
                "participants": participants,
            },
        )

    def form_valid(self, form):
        pariticipant_list = self.request.session["participant_data"]
        exclude_dict = json.loads(self.request.POST["excludes"])
        event = Event.objects.get(id=self.request.session["event_data"]["event_id"])
        participant_dict = {}
        for participant in pariticipant_list:
            participant_dict[participant[1]] = participant[0]

        print(participant_dict)
        print(type(exclude_dict))
        for exclude in exclude_dict:
            print(exclude)
            # user = CustomUser.objects.get(email=participant_dict[exclude])
            participant = Participant.objects.get(name=exclude, event=event)
            for excluded in exclude_dict[exclude]:
                # user_excluded = CustomUser.objects.get(email=participant_dict[excluded])
                excluded_participant = Participant.objects.get(
                    name=excluded, event=event
                )
                print(f"{participant}: {excluded_participant}")
                Exclusion.objects.create(
                    event=event,
                    participant=participant,
                    excluded_participant=excluded_participant,
                )
            print("----")
        return redirect(self.success_url)
