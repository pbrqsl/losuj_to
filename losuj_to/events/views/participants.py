import ast
import json
from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import DeleteView, FormView
from events.forms import (
    BulkUserRegistrationForm,
    BultUserRegistrationFormOld,
    ExcludeParticipantsForm,
    WhishCreateForm,
)
from events.helpers import get_event_by_pk
from events.mixins import EventOwnerMixin
from events.models import Event, Exclusion, Participant, Wish
from users.forms import BultUserRegistrationForm
from users.models import CustomUser


class ParticipantCreateView(FormView, SuccessMessageMixin, LoginRequiredMixin):
    template_name = "event/participant_information.html"
    form_class = BulkUserRegistrationForm
    success_url = "event_excludes"
    success_message = "yup"
    num_rows = 3

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any):
        form = self.form_class
        event_data = self.request.session["event_data"]

        if request.GET.get("participants"):
            participants = ast.literal_eval(request.GET.get("participants"))
            return render(
                self.request,
                self.template_name,
                context={
                    "form": form,
                    "event_data": event_data,
                    "participants": participants,
                },
            )

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
        event_id = self.request.session.get("event_data").get("event_id")
        event = get_object_or_404(Event, id=event_id)

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
                user = CustomUser.objects.create_user(email=email, password=None)

            participant, created = Participant.objects.get_or_create(
                user=user, event=event, name=name
            )
            parcipants_data.append([email, name])

        self.request.session["participant_data"] = parcipants_data
        return redirect(self.success_url)

    def form_invalid(self, form):
        event_data = self.request.session["event_data"]
        raw_participants = form.data["participants"].split("\n")
        participants = []
        for participant in raw_participants:
            email = participant.split(",")[0].rstrip()
            name = participant.split(",")[1].rstrip()
            participants.append([email, name])

        return render(
            self.request,
            self.template_name,
            context={
                "form": form,
                "event_data": event_data,
                "participants": participants,
                "rows_range": range(self.num_rows),
            },
        )


class ParticipantUpdateView(EventOwnerMixin, FormView, LoginRequiredMixin):
    template_name = "event/participant_information.html"
    form_class = BulkUserRegistrationForm
    num_rows = 3
    success_url = "event_summary"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        event_id = self.kwargs.get("pk")
        event = get_event_by_pk(event_id=event_id)

        if event.confirmed:
            return HttpResponseNotAllowed("Not allowed")

        event_data = {}
        event_data["event_name"] = event.event_name
        event_data["event_location"] = ""
        event_data["event_id"] = event.id
        participants_from_db = Participant.objects.filter(event=event)

        participants = []
        for participant in participants_from_db:
            participants.append([participant.user.email, participant.name])

        return render(
            request,
            self.template_name,
            context={
                "event_data": event_data,
                "participants": participants,
                "rows_range": range(self.num_rows),
            },
        )

    def form_valid(self, form):
        event_id = self.kwargs.get("pk")
        event = get_event_by_pk(event_id=event_id)
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
                user = CustomUser.objects.create_user(email=email, password=None)
            try:
                participant = Participant.objects.get(
                    user=user,
                    event=event,
                )
                participant.name = name
                participant.save()

            except ObjectDoesNotExist:
                participant = Participant.objects.create(
                    user=user, event=event, name=name
                )

            parcipants_data.append([email, name])

        participants_list = Participant.objects.filter(event=event)
        email_list = [data[0] for data in parcipants_data]

        for participant in participants_list:
            if participant.user.email not in email_list:
                participant.delete()

        self.request.session["participant_data"] = parcipants_data
        return redirect(self.success_url, pk=self.kwargs.get("pk"))

    def form_invalid(self, form):
        event_data = self.request.session["event_data"]
        raw_participants = form.data["participants"].split("\n")
        participants = []
        for participant in raw_participants:
            email = participant.split(",")[0].rstrip()
            name = participant.split(",")[1].rstrip()
            participants.append([email, name])

        return render(
            self.request,
            self.template_name,
            context={
                "form": form,
                "event_data": event_data,
                "participants": participants,
                "rows_range": range(self.num_rows),
            },
        )


class ParticipantExcludeCreateView(FormView, SuccessMessageMixin, LoginRequiredMixin):
    template_name = "event/excludes_information.html"
    form_class = ExcludeParticipantsForm
    success_url = "event_summary"
    success_message = "yup"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = self.form_class

        event_data = self.request.session["event_data"]
        event_id = self.request.session["event_data"]["event_id"]

        participants = []

        participants_queryset = Participant.objects.filter(event_id=event_id)

        for participant_item in participants_queryset:
            participants.append([participant_item.user.email, participant_item.name])

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
        event_id = self.request.session["event_data"]["event_id"]
        event = get_object_or_404(Event, id=event_id)

        success_url = reverse(self.success_url, kwargs={"pk": event.id})
        if self.request.POST["excludes"] == "{}":
            self.request.session["excludes"] = "{}"

            return redirect(success_url)
        exclude_dict = json.loads(self.request.POST["excludes"])
        self.request.session["excludes"] = exclude_dict

        for exclude in exclude_dict:
            participant = get_object_or_404(
                Participant, user__email=exclude, event=event
            )

            for excluded in exclude_dict[exclude]:
                excluded_participant = get_object_or_404(
                    Participant, user__email=excluded, event=event
                )

                Exclusion.objects.create(
                    event=event,
                    participant=participant,
                    excluded_participant=excluded_participant,
                )
        return redirect(success_url)


class ParticipantExcludeUpdateView(EventOwnerMixin, FormView, LoginRequiredMixin):
    template_name = "event/excludes_information.html"
    form_class = ExcludeParticipantsForm
    success_url = "event_summary"
    success_message = "yup"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        event_id = self.kwargs.get("pk")
        event = get_event_by_pk(event_id=event_id)
        if event.confirmed:
            return HttpResponseNotAllowed("Not allowed")

        draw_date = (
            event.draw_date.strftime("%Y-%m-%dT%H:%M:%S") if event.draw_date else None
        )

        event_date = event.event_date.strftime("%Y-%m-%d") if event.event_date else None

        event_data = {
            "event_name": event.event_name,
            "event_location": "",
            "event_date": event_date,
            "draw_date": draw_date,
            "price_limit": event.price_limit,
            "price_currency": event.price_currency,
            "event_id": event.id,
        }
        self.request.session["event_data"] = event_data

        participants = []
        excludes = {}

        participants_queryset = Participant.objects.filter(event_id=event_id)
        for participant_item in participants_queryset:
            participants.append([participant_item.user.email, participant_item.name])

        excludes_queryset = Exclusion.objects.filter(event_id=event_id)

        for exclude in excludes_queryset:
            if exclude.participant.user.email not in excludes:
                excludes[exclude.participant.user.email] = [
                    exclude.excluded_participant.user.email
                ]
            else:
                excludes[exclude.participant.user.email].append(
                    exclude.excluded_participant.user.email
                )

        return render(
            request,
            self.template_name,
            context={
                "event_data": event_data,
                "participants": participants,
                "excludes": excludes,
            },
        )

    def form_valid(self, form):
        event_id = self.kwargs.get("pk")
        event = get_event_by_pk(event_id=event_id)
        success_url = reverse(self.success_url, kwargs={"pk": event.id})
        exclude_dict = json.loads(self.request.POST["excludes"])
        self.request.session["excludes"] = exclude_dict

        exclusion_pairs = []
        for exclude in exclude_dict:
            participant = get_object_or_404(
                Participant, user__email=exclude, event=event
            )

            for excluded in exclude_dict[exclude]:
                exclusion_pairs.append([exclude, excluded])
                excluded_participant = get_object_or_404(
                    Participant, user__email=excluded, event=event
                )

                exclusion, created = Exclusion.objects.get_or_create(
                    event=event,
                    participant=participant,
                    excluded_participant=excluded_participant,
                )

        excludes_queryset = Exclusion.objects.filter(event=event)
        for exclude in excludes_queryset:
            exclude_pair = [
                exclude.participant.user.email,
                exclude.excluded_participant.user.email,
            ]
            if exclude_pair in exclusion_pairs:
                continue
            Exclusion.delete(exclude)
        return redirect(success_url)


class ParticipantWhishCreateView(FormView, LoginRequiredMixin):
    form_class = WhishCreateForm
    success_url = "event_view"
    template_name = "event/event_whish_create.html"

    def form_valid(self, form):
        event_id = self.kwargs.get("pk")
        event = get_event_by_pk(event_id=event_id)
        success_url = reverse(self.success_url, kwargs={"pk": event.id})
        participant = get_object_or_404(
            Participant, user__email=self.request.user.email, event=event
        )
        description = form.cleaned_data["description"]
        print(event)
        print(participant)
        print(description)
        Wish.objects.create(
            event=event, description=description, participant=participant
        )

        return redirect(success_url)


class ParticipantWishDeleteView(DeleteView, LoginRequiredMixin):
    model = Wish
    template_name = "template/whish_confirm_delete.html"

    def get_success_url(self) -> str:
        event_id = self.kwargs.get("event_id")
        success_url = reverse(
            "event_view",
            kwargs={"pk": event_id},
        )
        return success_url

    def get_queryset(self) -> QuerySet[Any]:
        whish_id = self.kwargs.get("pk")
        return Wish.objects.filter(id=whish_id)

    def delete(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()
        self.object.delete()
        success_url = self.get_success_url()
        return redirect(success_url)


class BulkUserRegistration(FormView):
    form_class = BultUserRegistrationFormOld
    template_name = "event/bulk_registration.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = BultUserRegistrationForm()
        return render(request, self.template_name, context={"form": form})

    def form_valid(self, form: Any) -> HttpResponse:
        new_users = []

        for row in form.cleaned_data["new_users"]:
            email = row.split(",")[0]

            if CustomUser.objects.filter(email=email):
                continue
            try:
                user = CustomUser.objects.create_user(email=email, password=None)
                new_users.append(user)

            except ValidationError:
                pass

        return render(
            self.request,
            "event/bulk_registration_confirm.html",
            {"new_users": new_users},
        )
