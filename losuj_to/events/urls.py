from django.urls import path
from events.views import (
    EventCreateView,
    EventExcludesCreate,
    EventParticipantsCreateView,
)

urlpatterns = [
    path("event_create/", EventCreateView.as_view(), name="event_create"),
    path(
        "event_create_participants/",
        EventParticipantsCreateView.as_view(),
        name="event_participants",
    ),
    path("event_excludes/", EventExcludesCreate.as_view(), name="event_excludes"),
]
