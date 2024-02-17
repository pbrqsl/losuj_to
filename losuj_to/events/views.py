import ast
import json
from typing import Any

from allauth.account.utils import has_verified_email
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import FormView, TemplateView
from events.forms import (
    BulkUserRegistrationForm,
    EventCreateForm,
    ExcludeParticipantsForm,
)
from events.models import Event, Exclusion, Participant
from users.models import CustomUser

from .helpers import get_event_by_pk


class EventCreateView(LoginRequiredMixin, FormView):
    form_class = EventCreateForm
    success_url = "event_participants"
    template_name = "event/event_information.html"

    def form_valid(self, form):
        event_data = form.cleaned_data
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
        self.request.session["create_state"] = "in_progress"
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
            price_currency=form.cleaned_data["price_currency"],
            price_limit=form.cleaned_data["price_limit"],
            draw_date=form.cleaned_data["draw_date"],
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
        # TODO: change this to dispatch
        user = self.request.user

        email = user.email or None

        if has_verified_email(user, email):
            return super().get(request, *args, **kwargs)
        messages.add_message(
            self.request,
            messages.ERROR,
            "This page is available for confirmed users only. \
                <a href='resend_confirmation_email/'>Resend confirmation email</a>",
        )
        return redirect("home")


class EventUpdateView(LoginRequiredMixin, FormView):
    form_class = EventCreateForm
    success_url = "event_summary"
    template_name = "event/event_information.html"

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        event_id = self.kwargs.get("pk")
        event = get_event_by_pk(event_id=event_id)
        if request.user != event.owner:
            raise PermissionDenied("You are not authorized!")
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self) -> dict[str, Any]:
        event_id = self.kwargs.get("pk")
        event = get_event_by_pk(event_id=event_id)
        return {
            "event_name": event.event_name,
            "event_location": event.event_location,
            "event_date": event.event_date,
            "draw_date": event.draw_date,
            "price_currency": event.price_currency,
            "price_limit": event.price_limit,
        }

    def form_valid(self, form: Any) -> HttpResponse:
        event_id = self.kwargs.get("pk")
        event = get_event_by_pk(event_id=event_id)

        event.event_name = form.cleaned_data["event_name"]
        event.event_location = form.cleaned_data["event_location"]
        event.event_date = form.cleaned_data["event_date"]
        event.price_currency = form.cleaned_data["price_currency"]
        event.price_limit = form.cleaned_data["price_limit"]
        event.save()

        return redirect(self.success_url, pk=self.kwargs.get("pk"))


class EventParticipantsCreateView(FormView, SuccessMessageMixin, LoginRequiredMixin):
    template_name = "event/participant_information.html"
    form_class = BulkUserRegistrationForm
    success_url = "event_excludes"
    success_message = "yup"
    num_rows = 3
    # exclude = "participants"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any):
        form = self.form_class
        event_data = self.request.session["event_data"]
        print(self.request.session.__dict__)
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
                # user = get_object_or_404(CustomUser, email=email)
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
            print(participant)
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


class EventParticipantsUpdateView(FormView, LoginRequiredMixin):
    template_name = "event/participant_information.html"
    form_class = BulkUserRegistrationForm
    num_rows = 3
    success_url = "event_summary"

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        event_id = self.kwargs.get("pk")
        event = get_event_by_pk(event_id=event_id)
        if request.user != event.owner:
            raise PermissionDenied("You are not authorized!")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        event_id = self.kwargs.get("pk")
        event = get_event_by_pk(event_id=event_id)
        event_data = {}
        event_data["event_name"] = event.event_name
        event_data["event_location"] = ""
        event_data["event_id"] = event.id
        participants_from_db = Participant.objects.filter(event=event)
        print(participants_from_db)
        participants = []
        for participant in participants_from_db:
            participants.append([participant.user.email, participant.name])
        print(event)
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
            created = False
            email = participant[0]
            name = participant[1]
            if name == "":
                name = participant[0]
            try:
                user = CustomUser.objects.get(email=email)
            except ObjectDoesNotExist:
                print("exception")
                user = CustomUser.objects.create_user(email=email, password=None)
            try:
                participant = Participant.objects.get(
                    user=user,
                    event=event,
                )
                participant.name = name
                participant.save()
                print(f"user {email} existed, data updated")
            except ObjectDoesNotExist:
                participant = Participant.objects.create(
                    user=user, event=event, name=name
                )
                created = True
                print(f"user {email} created")

            print(f"participant {email} existed: {created}")
            parcipants_data.append([email, name])

        participants_list = Participant.objects.filter(event=event)
        email_list = [data[0] for data in parcipants_data]
        print(email_list)
        for participant in participants_list:
            if participant.user.email not in email_list:
                print(f"{participant.user.email} to be removed!")
                participant.delete()

        self.request.session["participant_data"] = parcipants_data
        # return redirect(self.success_url)
        # if self.request.session["create_state"] != "in_progress":

        # return redirect("event_excludes")
        return redirect(self.success_url, pk=self.kwargs.get("pk"))

    def form_invalid(self, form):
        event_data = self.request.session["event_data"]
        raw_participants = form.data["participants"].split("\n")
        participants = []
        for participant in raw_participants:
            print(participant)
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


class EventExcludesCreate(FormView, SuccessMessageMixin, LoginRequiredMixin):
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
        # event = Event.objects.get(id=self.request.session["event_data"]["event_id"])
        event_id = self.request.session["event_data"]["event_id"]
        event = get_object_or_404(Event, id=event_id)

        success_url = reverse(self.success_url, kwargs={"pk": event.id})
        if self.request.POST["excludes"] == "{}":
            self.request.session["excludes"] = "{}"

            return redirect(success_url)
        # pariticipant_list = self.request.session["participant_data"]
        exclude_dict = json.loads(self.request.POST["excludes"])
        self.request.session["excludes"] = exclude_dict

        for exclude in exclude_dict:
            print(f'exclude: "{exclude}"')
            print(f"event: {event.id}")

            # participant = Participant.objects.get(user__email=exclude, event=event)
            participant = get_object_or_404(
                Participant, user__email=exclude, event=event
            )

            for excluded in exclude_dict[exclude]:
                # excluded_participant = Participant.objects.get(
                #     user__email=excluded, event=event
                # )
                excluded_participant = get_object_or_404(
                    Participant, user__email=excluded, event=event
                )
                print(f"{participant}: {excluded_participant}")
                Exclusion.objects.create(  # TODO 1: change to get_or_create
                    event=event,
                    participant=participant,
                    excluded_participant=excluded_participant,
                )
        return redirect(success_url)


class EventExcludesUpdate(FormView, LoginRequiredMixin):
    template_name = "event/excludes_information.html"
    form_class = ExcludeParticipantsForm
    success_url = "event_summary"
    success_message = "yup"

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        event_id = self.kwargs.get("pk")
        event = get_event_by_pk(event_id=event_id)
        if request.user != event.owner:
            raise PermissionDenied("You are not authorized!")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        event_id = self.kwargs.get("pk")
        event = get_event_by_pk(event_id=event_id)

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
        print(excludes_queryset)
        for exclude in excludes_queryset:
            print(exclude.participant.user.email)
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
        print(exclude_dict)
        exclusion_pairs = []
        for exclude in exclude_dict:
            # participant = Participant.objects.get(user__email=exclude, event=event)
            participant = get_object_or_404(
                Participant, user__email=exclude, event=event
            )

            for excluded in exclude_dict[exclude]:
                exclusion_pairs.append([exclude, excluded])
                # excluded_participant = Participant.objects.get(
                #     user__email=excluded, event=event
                # )
                excluded_participant = get_object_or_404(
                    Participant, user__email=excluded, event=event
                )
                print(f"{participant}: {excluded_participant}")
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


class EventSummarry(TemplateView, LoginRequiredMixin):
    template_name = "event/event_summary.html"

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        event_id = self.kwargs.get("pk")
        event = get_event_by_pk(event_id=event_id)
        if request.user != event.owner:
            raise PermissionDenied("You are not authorized!")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.request.session["create_state"] = "summary"
        event_id = self.kwargs.get("pk")
        event = get_event_by_pk(event_id=event_id)
        event_data = {
            "event_name": event.event_name,
            "event_location": "",
            "event_date": event.event_date,
            "draw_date": event.draw_date,
            "price_limit": event.price_limit,
            "price_currency": event.price_currency,
            "event_id": event.id,
            "confirmed": event.confirmed,
        }

        participants_queryset = Participant.objects.filter(event=event)
        participants = []
        excludes = {}
        for participant in participants_queryset:
            participants.append([participant.user.email, participant.name])

        excludes_queryset = Exclusion.objects.filter(event=event)
        if excludes_queryset and len(participants_queryset) < 4:
            messages.add_message(
                self.request,
                messages.ERROR,
                "The number of participants is currently to low to use exclude list. Please add participants to make excludes valid again.",
            )
        else:
            excludes = {}
            for exclude in excludes_queryset:
                if exclude.participant.name not in excludes:
                    excludes[exclude.participant.name] = []
                excludes[exclude.participant.name].append(
                    exclude.excluded_participant.name
                )

        drawing_pools = []
        for participant in participants_queryset:
            print(participant.id)
            participant_excludes = Exclusion.objects.filter(
                participant_id=participant.id
            ).filter(event_id=event_id)
            if not participant_excludes:
                print("not found excludes")
                exclude_pool = []
            else:
                print(participant_excludes)
                exclude_pool = [
                    exclude.excluded_participant for exclude in participant_excludes
                ]
                print(exclude_pool)

            drawing_pool = [
                candidate.id
                for candidate in participants_queryset
                if candidate != participant and candidate not in exclude_pool
            ]
            drawing_pools.append(drawing_pool)
            if len(drawing_pool) < 2:
                messages.add_message(
                    self.request,
                    messages.ERROR,
                    f"Exlusions for participant {participant} are to strict. Drawing names is not possible!",
                )

        print(excludes)
        print(drawing_pools)
        for drawing_pool in drawing_pools:
            if drawing_pools.count(drawing_pool) > len(drawing_pool):
                messages.add_message(
                    self.request,
                    messages.ERROR,
                    "Exlusions settings are to strict!",
                )
                break

        return render(
            request,
            self.template_name,
            context={
                "event_data": event_data,
                "participants": participants,
                "excludes": excludes,
            },
        )


class EventActivate(TemplateView, LoginRequiredMixin):
    success_url = "event_summary"

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        event_id = self.kwargs.get("pk")
        event = get_event_by_pk(event_id=event_id)
        if request.user != event.owner:
            raise PermissionDenied("You are not authorized!")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        event_id = self.kwargs.get("pk")
        event = get_event_by_pk(event_id=event_id)
        event.confirmed = True
        event.save()
        success_url = reverse(self.success_url, kwargs={"pk": event.id})
        participants_queryset = get_list_or_404(Participant, event_id=event.id)

        print(participants_queryset)
        drawing_pools = []
        for participant in participants_queryset:
            print(participant.id)
            excludes = Exclusion.objects.filter(participant_id=participant.id).filter(
                event_id=event_id
            )
            if not excludes:
                print("not found excludes")
                exclude_pool = []
            else:
                print(excludes)
                exclude_pool = [exclude.excluded_participant for exclude in excludes]
                print(exclude_pool)

            drawing_pool = [
                candidate.id
                for candidate in participants_queryset
                if candidate != participant and candidate not in exclude_pool
            ]
            print(f"drawing pool for participant {participant} {drawing_pool}")
            drawing_pools.append(drawing_pool)

        print(drawing_pools)

        # for participant in participants_queryset:
        #     print(participant.id)
        #     excludes = Exclusion.objects.filter(participant_id=participant.id).filter(event_id=event_id)
        #     if not excludes:
        #         print('not found excludes')
        #         exclude_pool = []
        #     else:
        #         print(excludes)
        #         exclude_pool = [exclude.excluded_participant for exclude in excludes]
        #         print(exclude_pool)
        #     draws = Draw.objects.filter(event=event)
        #     drawn_pool = [
        #         draw.drawn_participant for draw in draws
        #         ]

        #     print(drawn_pool)
        #     drawing_pool = [candidate.id for candidate in participants_queryset
        #                     if candidate != participant
        #                     and candidate not in exclude_pool
        #                     and candidate not in drawn_pool
        #                     ]
        #     print(drawing_pool)
        #     drawn_participant = get_object_or_404(Participant,id=random.choice(drawing_pool))
        #     print(drawn_participant)
        #     drawing_pools.append([participant, drawing_pool, len(drawing_pool)])

        print(drawing_pools)
        # sorted_drawing_pools = sorted(drawing_pools, key=lambda x: x[2])

        # Draw.objects.create(event=event,
        #     participant=participant,
        #     drawn_participant=drawn_participant)
        # print(sorted_drawing_pools)
        return redirect(success_url)

    #
    #
