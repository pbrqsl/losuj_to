from datetime import datetime, timedelta
from datetime import datetime
from itertools import chain
from operator import attrgetter
from typing import Any

import pytz
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import TemplateView
from events.helpers import get_and_validate_event, get_event_by_hash, get_event_by_pk
from events.mixins import EventOwnerMixin
from events.models import Draw, Event, Participant, Wish


class EventAdminDetailView(EventOwnerMixin, TemplateView, LoginRequiredMixin):
    template_name = "event/event_summary.html"

    def get_draws(self, event: Event):
        draws = Draw.objects.filter(event=event)
        return draws

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

        draws = self.get_draws(event)

        for draw in draws:
            for participant in participants:
                if participant[0] == draw.participant.user.email:
                    participant.append(draw.collected)

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
                "draws": draws,
            },
        )


class EventUserDetailView(TemplateView, LoginRequiredMixin):
    template_name = "event/participant_event_view.html"

    def get_event(self):
        event_id = self.kwargs.get("pk")
        event_hash = self.kwargs.get("hash")

        if event_id is not None:
            return get_event_by_pk(event_id=event_id)
        elif event_hash is not None:
            return get_event_by_hash(event_hash=event_hash)
        else:
            raise Http404

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        event = self.get_event()
        can_collect = False

        if not event.confirmed:
            messages.add_message(
                self.request,
                messages.ERROR,
                "The event you are looking for does not exist or is not active!",
            )
            return redirect(reverse("home"))
            raise Http404

        if event.draw_date:
            datetime_now = datetime.now()
            local_timezone = pytz.timezone("Europe/Berlin")
            datetime_now = datetime_now.astimezone(local_timezone)
            datetime_now = datetime_now.replace(tzinfo=None)
            drawing_date = event.draw_date
            drawing_date = drawing_date.replace(tzinfo=None)

            if drawing_date <= datetime_now:
                can_collect = True
        else:
            can_collect = True

        participant = get_object_or_404(
            Participant, user__email=self.request.user.email, event=event
        )
        draw = get_object_or_404(Draw, event=event, participant=participant)

        participant_wishes = Wish.objects.filter(event=event, participant=participant)
        drawn_paricipant_wishes = Wish.objects.filter(
            event=event, participant=draw.drawn_participant
        )

        event_validate = get_and_validate_event(event)
        participants = event_validate["participants"]
        print(participants)
        
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
            "drawn_participant_id": draw.drawn_participant.id,
            "participant": participant.name,
            "can_collect": can_collect,
            "draw_id": draw.id,
            "participant_wishes": participant_wishes,
            "drawn_participant_wishes": drawn_paricipant_wishes,
            "participants": participants,
        }

        return render(request, self.template_name, context={"event_data": event_data})


class EventListView(LoginRequiredMixin, TemplateView):
    template_name = "event/event_list.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        owned_events = Event.objects.filter(owner=request.user)
        participating = Participant.objects.filter(user__email=request.user).filter(
            event__confirmed=True
        )
        # participating = Participant.objects.filter(user__email=request.user)
        participated_events = []

        participating_events_list = participating.values_list(
            "event", flat=True
        ).distinct()

        drawing_statuses = {}
        participated_events = Event.objects.filter(pk__in=participating_events_list)

        local_timezone = pytz.timezone("Europe/Berlin")
        datetime_now = datetime.now()
        datetime_now = datetime_now.astimezone(local_timezone)
        datetime_now = datetime_now.replace(tzinfo=None)

        events_dict = {}
        for event in owned_events:
            event_class = "event-item"
            events_dict[event.id] = {
                "event_name": event.event_name,
                "owner": event.owner.email,
                "owned": True,
                "event_date": event.event_date,
                "event_draw_date": event.draw_date,
                "participated": False,
                "draw_collected": False,
                "event_confirmed": event.confirmed,
            }
            drawing_date = event.draw_date
            if isinstance(drawing_date, datetime):
                drawing_date = drawing_date.replace(tzinfo=None)
            else:
                drawing_date = datetime_now

            events_dict[event.id]["show_draw_date"] = (
                True if drawing_date > datetime_now else False
            )
            date_now = datetime.now().date()
            days_till_event = event.event_date - date_now

            if days_till_event < timedelta(days=-7):
                event_class += " older-than-7"
            events_dict[event.id]["event_class"] = event_class

        for event in participated_events:
            event_class = "event-item"
            drawing_status = Draw.objects.get(
                event=event, participant__user=request.user
            ).collected
            drawing_statuses[str(event.id)] = drawing_status

            if event.id in events_dict:
                events_dict[event.id]["participated"] = True
                events_dict[event.id]["draw_collected"] = drawing_status
            else:
                events_dict[event.id] = {
                    "event_name": event.event_name,
                    "owner": event.owner.email,
                    "owned": False,
                    "event_date": event.event_date,
                    "event_draw_date": event.draw_date,
                    "participated": True,
                    "draw_collected": drawing_status,
                    "event_confirmed": event.confirmed,
                }
            drawing_date = event.draw_date
            if isinstance(drawing_date, datetime):
                drawing_date = drawing_date.replace(tzinfo=None)
            else:
                drawing_date = datetime_now

            events_dict[event.id]["show_draw_date"] = (
                True if drawing_date > datetime_now else False
            )
            date_now = datetime.now().date()
            days_till_event = event.event_date - date_now
            if days_till_event < timedelta(days=-7):
                event_class += " older-than-7"
            events_dict[event.id]["event_class"] = event_class

        events_list = []
        for key in events_dict:
            events_dict[key]["id"] = key
            events_list.append(events_dict[key])

        events_list_by_date = sorted(events_list, key=lambda d: d["event_date"])

        local_timezone = pytz.timezone("Europe/Berlin")

        return render(
            request,
            self.template_name,
            context={

                "events_list": events_list_by_date,
                "datetime_now": datetime_now,
            },
        )
