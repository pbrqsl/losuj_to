from django.urls import path
from events.views import (
    EventExcludesInformation,
    EventInformationView,
    EventParticipantsInformationView,
)

urlpatterns = [
    path("event_create/", EventInformationView.as_view(), name="event_create"),
    path(
        "event_create_participants/",
        EventParticipantsInformationView.as_view(),
        name="event_participants",
    ),
    path("event_excludes/", EventExcludesInformation.as_view(), name="event_excludes"),
    # path("logout/", logout_view, name="logout"),
]
