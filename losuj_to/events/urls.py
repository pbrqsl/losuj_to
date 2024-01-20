from django.urls import path
from events.views import (
    EventCreateView,
    EventExcludesCreate,
    EventExcludesUpdate,
    EventParticipantsCreateView,
    EventParticipantsUpdateView,
    EventSummarry,
)

urlpatterns = [
    path("event_create/", EventCreateView.as_view(), name="event_create"),
    path(
        "event_create_participants/",
        EventParticipantsCreateView.as_view(),
        name="event_participants",
    ),
    path("event_excludes/", EventExcludesCreate.as_view(), name="event_excludes"),
    path("event_summary/<int:pk>", EventSummarry.as_view(), name="event_summary"),
    path(
        "event_update_participants/<int:pk>",
        EventParticipantsUpdateView.as_view(),
        name="event_participants_update",
    ),
    path(
        "event_update_excludes/<int:pk>",
        EventExcludesUpdate.as_view(),
        name="event_excludes_update",
    ),
    # path("event_excludes_update/")
]
