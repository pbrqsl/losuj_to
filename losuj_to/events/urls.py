from django.urls import path
from events.views import EventInformationView, EventParticipantsInformationView

urlpatterns = [
    path("event_create/", EventInformationView.as_view(), name="event_create"),
    path(
        "event_create_participants/",
        EventParticipantsInformationView.as_view(),
        name="event_participants",
    ),
    # path("logout/", logout_view, name="logout"),
]
