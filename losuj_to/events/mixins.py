from typing import Any

from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from events.helpers import get_event_by_pk


class EventOwnerMixin:
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        event_id = self.kwargs.get("pk")
        print(event_id)
        event = get_event_by_pk(event_id=event_id)
        if request.user != event.owner:
            raise PermissionDenied("You are not authorized!")
        return super().dispatch(request, *args, **kwargs)
