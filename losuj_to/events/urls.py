from django.urls import path
from events.views import (
    EventActivate,
    EventCreateView,
    EventDeactivate,
    EventExcludesCreate,
    EventExcludesUpdate,
    EventParticipantsCreateView,
    EventParticipantsUpdateView,
    EventSummarry,
    EventUpdateView,
    ParticipantEventView,
)

urlpatterns = [
    path("event_create/", EventCreateView.as_view(), name="event_create"),
    path("event_update/<int:pk>", EventUpdateView.as_view(), name="event_update"),
    path(
        "event_create_participants/",
        EventParticipantsCreateView.as_view(),
        name="event_participants",
    ),
    path("event_excludes/", EventExcludesCreate.as_view(), name="event_excludes"),
    path("event_summary/<int:pk>", EventSummarry.as_view(), name="event_summary"),
    path("event_view/<int:pk>", ParticipantEventView.as_view(), name="event_view"),
    path(
        "event_view/<slug:hash>",
        ParticipantEventView.as_view(),
        name="event_view_by_hash",
    ),
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
    path(
        "event_toggle_active/<int:pk>",
        EventActivate.as_view(),
        name="event_toggle_active",
    ),
    path(
        "event_deactivate/<int:pk>",
        EventDeactivate.as_view(),
        name="event_deactivate",
    ),
    # path("event_excludes_update/")
]
