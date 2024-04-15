from celery import Celery
from celery.result import AsyncResult

# os.environ.setdefault("DJANGO_SETTING_MODULE", "my_celery.settings")


email_queue = Celery(
    "my_celery", broker="redis://redis:6379/0", backend="redis://redis:6379/0"
)
# email_queue.config_from_object("django.conf:settings", namespace="CELERY")
# email_queue.autodiscover_tasks()


# def send_invitation(request: HttpRequest, participant, event):

# time.sleep(1)


@email_queue.task()
def send_invitation_mail(subject, plain_message, from_email, to_email, html_content):
    from django.core import mail

    mail.send_mail(
        subject, plain_message, from_email, [to_email], html_message=html_content
    )
    # time.sleep(10)


def get_task_status(task_id):
    return AsyncResult(task_id)


# def send_invitation2():
#     time.sleep(4)
#     print('plum')
#     return 'email_sent'

# @email_queue.task()
# def send_invitation():
#     time.sleep(10)

#     return "SUCCESS"
