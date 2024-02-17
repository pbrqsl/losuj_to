from django.shortcuts import get_object_or_404

from .models import Event


def get_event_by_pk(event_id):
    return get_object_or_404(Event, id=event_id)
