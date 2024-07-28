from django.urls import path
from events.views import (
    EmailSendInvitationsWait,
    EmailSendInvitationsWaitStream,
    EventActivate,
    EventCreateView,
    EventDeactivate,
    EventExcludesCreate,
    EventExcludesUpdate,
    EventParticipantsCreateView,
    EventParticipantsUpdateView,
    EventSendInvitations,
    EventSendReminderSingle,
    EventSummarry,
    EventUpdateView,
    ListOfEvents,
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
    path(
        "send_invitations/<int:pk>",
        EventSendInvitations.as_view(),
        name="send_invitations",
    ),
    path(
        "send_reminder/<int:pk>/<int:participant_id>",
        EventSendReminderSingle.as_view(),
        name="send_reminder",
    ),
    path(
        "send_invitations_wait/<int:pk>/<str:task_ids>",
        EmailSendInvitationsWait.as_view(),
        name="send_invitations_wait",
    ),
    path(
        "event_list/",
        ListOfEvents.as_view(),
        name="event_list",
    ),
    path(
        "status_stream/<int:pk>/<str:task_ids>",
        EmailSendInvitationsWaitStream.as_view(),
        name="event_send_invitation_status_stream",
    ),
]
