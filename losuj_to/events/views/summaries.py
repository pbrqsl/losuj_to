from datetime import datetime
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
from events.models import Draw, Event, Participant, Whish


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

        participant_whishes = Whish.objects.filter(event=event, participant=participant)
        drawn_paricipant_whishes = Whish.objects.filter(
            event=event, participant=draw.drawn_participant
        )

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
            "participant_whishes": participant_whishes,
            "drawn_participant_whishes": drawn_paricipant_whishes,
        }

        return render(request, self.template_name, context={"event_data": event_data})


class EventListView(LoginRequiredMixin, TemplateView):
    template_name = "event/event_list.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        owned_events = Event.objects.filter(owner=request.user)
        participating = Participant.objects.filter(user__email=request.user)
        participated_events = []

        participating_events_list = participating.values_list(
            "event", flat=True
        ).distinct()

        participated_events = Event.objects.filter(pk__in=participating_events_list)

        return render(
            request,
            self.template_name,
            context={
                "owned_events": owned_events,
                "participated_events": participated_events,
            },
        )
