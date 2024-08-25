import time
from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import TemplateView
from events.celery_app import get_task_status
from events.helpers import (
    get_event_by_pk,
    get_participant_by_id,
    send_invitation,
    send_raminder,
)
from events.mixins import EventOwnerMixin
from events.models import EmailTask, Participant


class InvitationSendView(EventOwnerMixin, TemplateView, LoginRequiredMixin):
    success_url = "send_invitations_wait"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        event_id = self.kwargs.get("pk")
        event = get_event_by_pk(event_id=event_id)
        participants = Participant.objects.filter(event_id=event.id)
        email_tasks = []
        for participant in participants:
            email_task_job = send_invitation(
                request=request, participant=participant, event=event
            )

            email_tasks.append(email_task_job.id)
            email_task = EmailTask(
                task_uuid=email_task_job.id,
                owner=event.owner,
                event=event,
                email=participant.user.email,
                status="PEN",
            )
            email_task.save()

        email_tasks = ",".join(email_tasks)
        success_url = reverse(
            self.success_url,
            kwargs={
                "pk": event.id,
                "task_ids": email_tasks,
            },
        )
        return redirect(success_url)


class InvitationReminderView(EventOwnerMixin, TemplateView, LoginRequiredMixin):
    success_url = "send_invitations_wait"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        event_id = self.kwargs.get("pk")
        participant_id = self.kwargs.get("participant_id")
        event = get_event_by_pk(event_id=event_id)
        participant = get_participant_by_id(participant_id=participant_id)
        email_tasks = []

        email_task_job = send_raminder(
            request=request, participant=participant, event=event
        )

        email_tasks.append(email_task_job.id)
        email_task = EmailTask(
            task_uuid=email_task_job.id,
            owner=event.owner,
            event=event,
            email=participant.user.email,
            status="PEN",
        )
        email_task.save()

        email_tasks = ",".join(email_tasks)
        success_url = reverse(
            self.success_url,
            kwargs={
                "pk": event.id,
                "task_ids": email_tasks,
            },
        )
        return redirect(success_url)


class InvitationWaitView(EventOwnerMixin, TemplateView, LoginRequiredMixin):
    success_url = "event_send_invitation_status_stream"
    template_name = "event/event_invitation_wait.html"
    redirect_url = "event_summary"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        task_ids = self.kwargs.get("task_ids")
        event_id = self.kwargs.get("pk")
        task_ids_array = task_ids.split(",")
        for task_id in task_ids_array:
            task = get_object_or_404(EmailTask, task_uuid=task_id)
            if task.owner != request.user:
                raise PermissionDenied

        email_tasks_pending = EmailTask.objects.filter(event_id=event_id, status="PEN")

        if len(email_tasks_pending) == 0:
            redirect_url = reverse(self.redirect_url, kwargs={"pk": event_id})
            messages.add_message(
                self.request,
                messages.INFO,
                "Invite sent",
            )
            return redirect(redirect_url)

        return render(
            self.request,
            self.template_name,
            {"task_ids": task_ids, "event_id": event_id},
        )


class InvitationStreamWaitView(TemplateView, LoginRequiredMixin):
    success_url = "event_summary"

    def email_status_set_OK(self, task_id):
        email_task = EmailTask.objects.get(task_uuid=task_id)
        email_task.status = "OK"
        email_task.save()

    def get_task_state(self, task_id):
        task_status = get_task_status(task_id=task_id)
        return task_status.state

    def event_stream(self, request, task_ids):
        task_ids_converted = task_ids.split(",")
        waiting = True
        no_of_tasks = len(task_ids_converted)
        no_of_tasks_completed = 0
        while waiting:
            print("sending mail")
            time.sleep(1)
            for task_id in task_ids_converted:
                task_state = self.get_task_state(task_id=task_id)
                if task_state == "PENDING":
                    body = f"{task_id}: {task_state}"
                    yield f"data: {body}\n\n"
                else:
                    self.email_status_set_OK(task_id=task_id)
                    no_of_tasks_completed += 1
                    if no_of_tasks_completed == no_of_tasks:
                        body = "Emails sent"
                        request.session["email_status"] = "done"
                        waiting = False
                    else:
                        body = f"{task_id}: {task_state}"
                    yield f"data: {body}\n\n"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        task_ids = self.kwargs.get("task_ids")
        return StreamingHttpResponse(
            self.event_stream(request, task_ids=task_ids),
            content_type="text/event-stream",
        )
