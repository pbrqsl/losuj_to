from datetime import datetime
from typing import Any

from allauth.account.utils import has_verified_email
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import FormView, TemplateView
from events.drawing.drawing import perform_drawing
from events.forms import (
    EventConfirmActivationForm,
    EventConfirmDeactivationForm,
    EventCreateForm,
)
from events.helpers import confirm_event, get_and_validate_event, get_event_by_pk
from events.mixins import EventOwnerMixin
from events.models import Draw, Event


class EventCreateView(LoginRequiredMixin, FormView):
    form_class = EventCreateForm
    success_url = "event_participants"
    template_name = "event/event_information.html"

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        user = self.request.user
        email = user.email or None

        if has_verified_email(user, email):
            return render(
                self.request,
                self.template_name,
                context={
                    "form": self.form_class,
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
        if not self.request.POST["draw_date"]:
            return super().post(request, *args, **kwargs)

        return super().post(request, *args, **kwargs)

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


class EventUpdateView(EventOwnerMixin, LoginRequiredMixin, FormView):
    form_class = EventCreateForm
    success_url = "event_summary"
    template_name = "event/event_information.html"

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
        event.draw_date = form.cleaned_data["draw_date"]
        event.price_currency = form.cleaned_data["price_currency"]
        event.price_limit = form.cleaned_data["price_limit"]
        event.save()

        return redirect(self.success_url, pk=self.kwargs.get("pk"))


class EventActivateView(EventOwnerMixin, TemplateView, LoginRequiredMixin):
    form_class = EventConfirmActivationForm
    success_url = "send_invitations"
    no_action_url = "event_summary"
    template_name = "event/event_confirm_activation.html"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        form = self.form_class()
        event_id = self.kwargs.get("pk")
        event = get_event_by_pk(event_id=event_id)
        date_now = datetime.now().date()
        event_validate = get_and_validate_event(event=event)
        participants = event_validate["participants"]

        no_action_url = reverse(self.no_action_url, kwargs={"pk": event.id})

        if event.event_date < date_now:
            messages.add_message(
                self.request,
                messages.ERROR,
                "You cannot activate the event which occurs in the past!",
            )

            return redirect(no_action_url)

        if len(participants) < 3:
            messages.add_message(
                self.request,
                messages.ERROR,
                "The number of participants is not correct.",
            )

            return redirect(no_action_url)

        return render(request, self.template_name, {"form": form})

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        event_id = self.kwargs.get("pk")
        event = get_event_by_pk(event_id=event_id)

        success_url = reverse(self.success_url, kwargs={"pk": event.id})
        no_action_url = reverse(self.no_action_url, kwargs={"pk": event.id})
        event_validate = get_and_validate_event(event=event)
        if not event_validate["is_valid"]:
            return redirect(no_action_url)

        if event.confirmed:
            return redirect(no_action_url)

        confirm_event(event=event)

        drawing_dict = event_validate["drawing_dict"]
        participants = event_validate["participants"]

        perform_drawing(
            event=event, participants=participants, drawing_dict=drawing_dict
        )

        return redirect(success_url)


class EventDeactivateView(EventOwnerMixin, TemplateView, LoginRequiredMixin):
    form_class = EventConfirmDeactivationForm
    success_url = "event_summary"
    template_name = "event/event_confirm_deactivation.html"

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        event_id = self.kwargs.get("pk")
        event = get_event_by_pk(event_id=event_id)
        success_url = reverse(self.success_url, kwargs={"pk": event.id})

        if not event.confirmed:
            return redirect(success_url)

        draw_results = Draw.objects.filter(event=event)
        draw_results.delete()

        event.confirmed = False
        event.confirmed_date = None
        event.save()

        return redirect(success_url)
