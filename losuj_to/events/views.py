import ast
import json
from datetime import datetime
from typing import Any

import pytz
from allauth.account.utils import has_verified_email
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core import mail
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags
from django.views.generic import FormView, TemplateView
from events.forms import (
    BulkUserRegistrationForm,
    EventConfirmActivationForm,
    EventConfirmDeactivationForm,
    EventCreateForm,
    ExcludeParticipantsForm,
)
from events.models import Draw, Event, Exclusion, Participant
from users.models import CustomUser

from .helpers import (
    event_draw,
    get_and_validate_event,
    get_event_by_hash,
    get_event_by_pk,
)


class EventCreateView(LoginRequiredMixin, FormView):
    form_class = EventCreateForm
    success_url = "event_participants"
    template_name = "event/event_information.html"

    # common_timezones = {
    # "London": "Europe/London",
    # "Paris": "Europe/Paris",
    # "New York": "America/New_York",
    # }

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        # TODO: change this to dispatch
        user = self.request.user

        email = user.email or None

        if has_verified_email(user, email):
            # return super().get(request, *args, **kwargs)
            return render(
                self.request,
                self.template_name,
                context={
                    "form": self.form_class,
                    # "timezones": self.common_timezones,
                },
            )
        messages.add_message(
            self.request,
            messages.ERROR,
            "This page is available for confirmed users only. \
                <a href='resend_confirmation_email/'>Resend confirmation email</a>",
        )
        return redirect("home")

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        # print(self.request.POST["timezone"])
        if not self.request.POST["draw_date"]:
            return super().post(request, *args, **kwargs)

        # draw_date = parse_datetime(self.request.POST["draw_date"])
        # request.session["django_timezone"] = request.POST["timezone"]

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        event_data = form.cleaned_data
        print(form.cleaned_data)
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
        print("form invalid")
        return render(
            self.request,
            self.template_name,
            context={"form": form},
        )


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
        print(participants_queryset)
        for participant_item in participants_queryset:
            participants.append([participant_item.user.email, participant_item.name])
        print(participants)
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

        event_validate = get_and_validate_event(event)
        participants = event_validate["participants"]
        excludes = event_validate["excludes"]
        errors = event_validate["errors"]

        for error in errors:
            messages.add_message(
                self.request,
                messages.ERROR,
                error,
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


class EventActivate(TemplateView, LoginRequiredMixin):
    form_class = EventConfirmActivationForm
    success_url = "event_summary"
    template_name = "event/event_confirm_activation.html"

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        event_id = self.kwargs.get("pk")
        event = get_event_by_pk(event_id=event_id)
        if request.user != event.owner:
            raise PermissionDenied("You are not authorized!")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        print("post")
        event_id = self.kwargs.get("pk")
        event = get_event_by_pk(event_id=event_id)
        success_url = reverse(self.success_url, kwargs={"pk": event.id})
        event_validate = get_and_validate_event(event=event)
        # print(event_validate)
        if not event_validate["is_valid"]:
            print("not valid!")
            return redirect(success_url)
        if event.confirmed:
            print("event already active!")
            return redirect(success_url)

        event.confirmed = True
        event.save()

        # def event_draw(drawing_dict, participants):
        #     print('draw with function!')
        #     counter = 0
        #     continue_drawing = True
        #     while continue_drawing:
        #         counter += 1
        #         print(f"try no {counter}")
        #         if counter == 100:
        #             continue_drawing = False
        #         drawn_participants = []
        #         draw_result = {}
        #         for participant in participants:
        #             drawing_pool = [
        #                 x
        #                 for x in drawing_dict[participant[0]]
        #                 if x not in drawn_participants
        #             ]
        #             if len(drawing_pool) == 0:
        #                 print("not succeded")
        #                 continue
        #             drawn_participant = random.choice(drawing_pool)
        #             drawn_participants.append(drawn_participant)
        #             draw_result[participant[0]] = drawn_participant

        #         if len(draw_result) == len(participants):
        #             continue_drawing = False
        #     return draw_result

        drawing_dict = event_validate["drawing_dict"]
        participants = event_validate["participants"]

        draw_result = event_draw(drawing_dict=drawing_dict, participants=participants)
        print(draw_result)

        for key in draw_result:
            participant = get_object_or_404(Participant, user__email=key, event=event)
            drawn_participant = get_object_or_404(
                Participant, user__email=draw_result[key], event=event
            )
            Draw.objects.create(
                participant=participant,
                drawn_participant=drawn_participant,
                event=event,
            )
            # print(f"{participant} drawn {drawn_participant}")
            # print(f"{participant.user.email} drawn {drawn_participant.user.email}")

        subject, from_email, to_email = (
            "Subject",
            "pbrqsl@gmail.com",
            "pbronikowski@gmail.com",
        )
        html_content = render_to_string(
            "event/email_template.html", {"context": "values"}
        )
        plain_message = strip_tags(html_content)

        mail.send_mail(
            subject, plain_message, from_email, [to_email], html_message=html_content
        )

        return redirect(success_url)


class EventDeactivate(TemplateView, LoginRequiredMixin):
    # set confirmed to FALSE
    # delete drawing results
    form_class = EventConfirmDeactivationForm
    success_url = "event_summary"
    template_name = "event/event_confirm_deactivation.html"

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        print("post")
        event_id = self.kwargs.get("pk")
        event = get_event_by_pk(event_id=event_id)
        success_url = reverse(self.success_url, kwargs={"pk": event.id})

        # event_validate = get_and_validate_event(event=event)

        if not event.confirmed:
            print("nothing to do")
            return redirect(success_url)

        draw_results = Draw.objects.filter(event=event)
        draw_results.delete()

        event.confirmed = False
        event.save()

        return redirect(success_url)


class ParticipantEventView(TemplateView, LoginRequiredMixin):
    template_name = "event/participant_event_view.html"

    def get_event(self):
        event_id = self.kwargs.get("pk")
        event_hash = self.kwargs.get("hash")

        if event_id is not None:
            print("by id")
            return get_event_by_pk(event_id=event_id)
        elif event_hash is not None:
            print("by hash")
            return get_event_by_hash(event_hash=event_hash)
        else:
            raise Http404

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        # event_id = self.kwargs.get("pk")
        event = self.get_event()
        can_collect = False

        if not event.confirmed:
            raise Http404

        if event.draw_date:
            utc_timezone = pytz.timezone("UTC")
            current_time = datetime.now()
            current_time = utc_timezone.localize(current_time)
            if event.draw_date < current_time:
                can_collect = True
        else:
            can_collect = True

        participant = get_object_or_404(
            Participant, user__email=self.request.user.email, event=event
        )
        draw = get_object_or_404(Draw, event=event, participant=participant)

        event_data = {
            "event_name": event.event_name,
            "event_location": "",
            "event_date": event.event_date,
            "draw_date": event.draw_date,
            "price_limit": event.price_limit,
            "price_currency": event.price_currency,
            "event_id": event.id,
            "draw_collected": draw.collected,
            "drawn_participant": draw.drawn_participant.name,
            "participant": participant.name,
            "can_collect": can_collect,
            "draw_id": draw.id,
        }
        print(event_data)
        return render(request, self.template_name, context={"event_data": event_data})
