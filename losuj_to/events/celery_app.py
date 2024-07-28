from datetime import datetime

from celery import Celery
from celery.result import AsyncResult
from celery.schedules import crontab
from celery.utils.log import get_task_logger

email_queue = Celery(
    "my_celery", broker="redis://redis:6379/0", backend="redis://redis:6379/0"
)


logger = get_task_logger("my_celery")


@email_queue.task()
def send_invitation_mail(subject, plain_message, from_email, to_email, html_content):
    from django.core import mail

    logger.info("sending email 12345678910!")
    logger.info(f"plain_message: {plain_message}")
    mail.send_mail(
        subject, plain_message, from_email, [to_email], html_message=html_content
    )


@email_queue.task()
def check_not_collected_draws():
    from events.models import Draw, Event

    event = Event.objects.get(id=8)
    logger.info(f"running background task {event}")
    subject = f"{event.id}, you are invited to {event.event_name}"  # noqa
    from_email = "pbrqsl@gmail.com"  # noqa
    to_email = "pbronikowski@gmail.com"  # noqa
    time_now = datetime.now().date()
    draws_not_collected = (
        Draw.objects.filter(event__event_date__gt=time_now)
        .filter(event__confirmed=True)
        .filter(collected=False)
    )
    for draw in draws_not_collected:
        event_date = draw.event.event_date
        time_diff = event_date - time_now
        logger.info(f"draws_date: {draw.event.event_date}")
        logger.info(f"days_diff: {time_diff.days}")

    logger.info(f"draws_not_collected: {draws_not_collected}")
    # task = send_invitation_mail.delay(
    #     subject=subject,
    #     plain_message=plain_message,
    #     from_email=from_email,
    #     to_email=to_email,
    #     html_content=html_content,

    # )
    return "scheduled task test"


@email_queue.task()
def time_to_event_1w():
    # your event starts in one week, go to the event page for details
    return "it's 22:12"


def get_task_status(task_id):
    return AsyncResult(task_id)


email_queue.conf.beat_schedule = {
    "check_not_collected_every_10_minutes": {
        "task": "events.celery_app.check_not_collected_draws",
        "schedule": 10.0,
    },
    "time_to_event_1w": {
        "task": "events.celery_app.time_to_event_1w",
        "schedule": crontab(hour=20, minute=15),
    },
}
