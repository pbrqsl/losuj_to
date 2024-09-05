from datetime import datetime

from django.shortcuts import get_list_or_404, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from events.celery_app import send_invitation_mail
from events.models import Event, Exclusion, Participant


def get_event_by_pk(event_id):
    # event = Event.objects.get(id=event_id)
    return get_object_or_404(Event, id=event_id)


def get_participant_by_id(participant_id):
    return get_object_or_404(Participant, id=participant_id)


def get_event_by_hash(event_hash):
    return get_object_or_404(Event, token=event_hash)


def get_exclude_pool(participant: Participant, event: Event):
    event_id = event.id
    participant_excludes = Exclusion.objects.filter(
        participant_id=participant.id
    ).filter(event_id=event_id)
    if not participant_excludes:
        return []
    return [exclude.excluded_participant for exclude in participant_excludes]


def exludes_queryset_to_dict(excludes_queryset):
    excludes = {}
    for exclude in excludes_queryset:
        if exclude.participant.name not in excludes:
            excludes[exclude.participant.name] = []
        excludes[exclude.participant.name].append(exclude.excluded_participant.name)
    return excludes


def get_and_validate_event(event: Event):
    is_valid = True
    participants_queryset = get_list_or_404(Participant, event=event)
    excludes_queryset = Exclusion.objects.filter(event=event)

    errors = []
    participants = []
    excludes = {}

    validation_result = {
        "is_valid": is_valid,
        "participants": participants,
        "excludes": excludes,
        "errors": errors,
    }

    for participant in participants_queryset:
        participants.append([participant.user.email, participant.name, participant.id])

    if excludes_queryset and len(participants_queryset) < 4:
        errors += (
            "The number of participants is currently to low to use exclude list. Please add participants to make excludes valid again.",
        )
        validation_result["is_valid"] = False
        return validation_result

    excludes = exludes_queryset_to_dict(excludes_queryset=excludes_queryset)

    drawing_pools = []
    drawing_dict = {}

    for participant in participants_queryset:
        exclude_pool = get_exclude_pool(participant=participant, event=event)

        drawing_pool = [
            candidate.user.email
            for candidate in participants_queryset
            if candidate != participant and candidate not in exclude_pool
        ]

        if len(drawing_pool) < 2:
            errors += (
                f"Exlusions for participant {participant} are to strict. Drawing names is not possible!",
            )
            validation_result["is_valid"] = False
            return validation_result

        drawing_pools.append(drawing_pool)
        drawing_dict[participant.user.email] = drawing_pool

    validation_result["excludes"] = excludes
    validation_result["drawing_dict"] = drawing_dict

    for drawing_pool in drawing_pools:
        if drawing_pools.count(drawing_pool) > len(drawing_pool):
            errors += ("Exlusions settings are to strict!",)
            validation_result["is_valid"] = False
            break

    return validation_result


def confirm_event(event):
    if not event.confirmed:
        event.confirmed = True
        event.confirmed_date = datetime.now().date()
        event.save()


def send_invitation(request, participant, event):
    from django.utils.html import strip_tags

    url_prefix = reverse("login")
    url_prefix = request.build_absolute_uri(url_prefix)
    invite_url = f"{url_prefix}?token={participant.user.user_token}&next=/events/event_view/{event.token}"
    subject = f"{participant.name}, you are invited to {event.event_name}"
    from_email = "pbrqsl@gmail.com"
    to_email = "pbronikowski@gmail.com"
    html_content = render_to_string(
        "event/email_template.html",
        {"invite_url": invite_url, "participant_name": participant.name},
    )
    plain_message = strip_tags(html_content)

    task = send_invitation_mail.delay(
        subject=subject,
        plain_message=plain_message,
        from_email=from_email,
        to_email=to_email,
        html_content=html_content,
    )
    return task


def send_raminder(request, participant, event):
    from django.utils.html import strip_tags

    url_prefix = reverse("login")
    url_prefix = request.build_absolute_uri(url_prefix)
    invite_url = f"{url_prefix}?token={participant.user.user_token}&next=/events/event_view/{event.token}"
    subject = f"{participant.name}, pelase visit the page of event: {event.event_name}"
    from_email = "pbrqsl@gmail.com"
    to_email = "pbronikowski@gmail.com"  #
    html_content = render_to_string(
        "event/email_template.html",
        {
            "invite_url": invite_url,
            "participant_name": participant.name,
            "event_name": event.event_name,
        },
    )
    plain_message = strip_tags(html_content)

    task = send_invitation_mail.delay(
        subject=subject,
        plain_message=plain_message,
        from_email=from_email,
        to_email=to_email,
        html_content=html_content,
    )
    return task


def send_raminder_whishes(request, participant, event):
    from django.utils.html import strip_tags

    url_prefix = reverse("login")
    url_prefix = request.build_absolute_uri(url_prefix)
    invite_url = f"{url_prefix}?token={participant.user.user_token}&next=/events/event_view/{event.token}"
    subject = f"{participant.name}, pelase visit the page of event: {event.event_name}"
    from_email = "pbrqsl@gmail.com"
    to_email = "pbronikowski@gmail.com"  #
    html_content = render_to_string(
        "event/email_template_whishes.html",
        {
            "invite_url": invite_url,
            "participant_name": participant.name,
            "event_name": event.event_name,
        },
    )
    plain_message = strip_tags(html_content)

    task = send_invitation_mail.delay(
        subject=subject,
        plain_message=plain_message,
        from_email=from_email,
        to_email=to_email,
        html_content=html_content,
    )
    return task
