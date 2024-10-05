from datetime import datetime, timedelta

from celery import Celery
from celery.result import AsyncResult
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from django.template.loader import render_to_string
from django.urls import reverse

email_queue = Celery(
    "my_celery", broker="redis://redis:6379/0", backend="redis://redis:6379/0"
)


logger = get_task_logger("my_celery")


@email_queue.task()
def send_invitation_mail(subject, plain_message, from_email, to_email, html_content):
    from django.core import mail

    mail.send_mail(
        subject, plain_message, from_email, [to_email], html_message=html_content
    )


@email_queue.task()
def check_not_collected_draws():
    import pytz
    from django.contrib.sites.models import Site
    from events.models import Draw

    draws_no_collected = Draw.objects.filter(event__confirmed=True).filter(
        collected=False
    )
    date_now = datetime.now().date()
    datetime_now = datetime.now()
    local_timezone = pytz.timezone("Europe/Berlin")
    datetime_now = datetime_now.astimezone(local_timezone)
    datetime_now = datetime_now.replace(tzinfo=None)

    event_reminder_days = [1, 2, 4, 7, 14, 20]

    for draw in draws_no_collected:
        date_confirmed = draw.event.confirmed_date
        days_since_confirmed = date_now - date_confirmed
        days_till_event = draw.event.event_date - date_now

        if isinstance(draw.event.draw_date, datetime):
            drawing_date = draw.event.draw_date
            drawing_date = drawing_date.replace(tzinfo=None)
            drawing_time_difference = drawing_date - datetime_now

        else:
            drawing_time_difference = timedelta(hours=-1)
            drawing_date = datetime_now

        for event_reminder_day in event_reminder_days:
            if (
                days_since_confirmed >= timedelta(days=2)
                and days_till_event == timedelta(days=event_reminder_day)
                and drawing_time_difference < timedelta(minutes=0)
            ):
                from_email = "pbrqsl@gmail.com"  # noqa
                to_email = "pbronikowski@gmail.com"  # noqa
                participant_name = draw.participant.name
                subject = f"{participant_name}, you are invited to {draw.event.event_name}"  # noqa
                plain_message = "plain message placeholder"
                url_prefix = reverse("login")
                user_token = draw.participant.user.user_token
                url_prefix = (Site.objects.get_current()).name
                invite_url = f"http://{url_prefix}/login/?token={user_token}&next=/events/event_view/{draw.event.token}"

                html_content = render_to_string(
                    "event/email_reminder__auto_days_template.html",
                    {
                        "invite_url": invite_url,
                        "participant_name": participant_name,
                        "days_left_count": days_till_event,
                    },
                )
                send_invitation_mail.delay(
                    subject=subject,
                    plain_message=plain_message,
                    from_email=from_email,
                    to_email=to_email,
                    html_content=html_content,
                )
    return "scheduled task test"


@email_queue.task()
def time_to_event_1w():
    return "it's 22:12"


def get_task_status(task_id):
    return AsyncResult(task_id)


email_queue.conf.beat_schedule = {
    "check_not_collected_every_10_minutes": {
        "task": "events.celery_app.check_not_collected_draws",
        "schedule": 3600.0,
    },
    "time_to_event_1w": {
        "task": "events.celery_app.time_to_event_1w",
        "schedule": crontab(hour=17, minute=6),
    },
    "time_to_event_1w_": {
        "task": "events.celery_app.time_to_event_1w",
        "schedule": crontab(hour=15, minute=35),
    },
}
