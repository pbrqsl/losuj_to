from django.urls import path
from events.views.crud import (
    EventActivateView,
    EventCreateView,
    EventDeactivateView,
    EventUpdateView,
)
from events.views.notifications import (
    InvitationReminderView,
    InvitationReminderWishesView,
    InvitationSendView,
    InvitationStreamWaitView,
    InvitationWaitView,
    InvitationWishesStreamWaitView,
    InvitationWishesWaitView,
)
from events.views.participants import (
    BulkUserRegistration,
    ParticipantCreateView,
    ParticipantExcludeCreateView,
    ParticipantExcludeUpdateView,
    ParticipantUpdateView,
    ParticipantWishCreateView,
    ParticipantWishDeleteView,
)
from events.views.summaries import (
    EventAdminDetailView,
    EventListView,
    EventUserDetailView,
)

urlpatterns = [
    path("event_create/", EventCreateView.as_view(), name="event_create"),
    path("event_update/<int:pk>", EventUpdateView.as_view(), name="event_update"),
    path(
        "event_create_participants/",
        ParticipantCreateView.as_view(),
        name="event_participants",
    ),
    path(
        "bulk_registration/",
        BulkUserRegistration.as_view(),
        name="bulk_registration",
    ),
    path(
        "event_excludes/", ParticipantExcludeCreateView.as_view(), name="event_excludes"
    ),
    path(
        "event_summary/<int:pk>", EventAdminDetailView.as_view(), name="event_summary"
    ),
    path("event_view/<int:pk>", EventUserDetailView.as_view(), name="event_view"),
    path(
        "event_view/<slug:hash>",
        EventUserDetailView.as_view(),
        name="event_view_by_hash",
    ),
    path(
        "event_update_participants/<int:pk>",
        ParticipantUpdateView.as_view(),
        name="event_participants_update",
    ),
    path(
        "event_update_excludes/<int:pk>",
        ParticipantExcludeUpdateView.as_view(),
        name="event_excludes_update",
    ),
    path(
        "event_wish_create/<int:pk>",
        ParticipantWishCreateView.as_view(),
        name="event_wish_create",
    ),
    path(
        "event_wish_delete/<int:pk>/<int:event_id>",
        ParticipantWishDeleteView.as_view(),
        name="event_wish_delete",
    ),
    path(
        "event_toggle_active/<int:pk>",
        EventActivateView.as_view(),
        name="event_toggle_active",
    ),
    path(
        "event_deactivate/<int:pk>",
        EventDeactivateView.as_view(),
        name="event_deactivate",
    ),
    path(
        "send_invitations/<int:pk>",
        InvitationSendView.as_view(),
        name="send_invitations",
    ),
    path(
        "send_reminder/<int:pk>/<int:participant_id>",
        InvitationReminderView.as_view(),
        name="send_reminder",
    ),
    path(
        "send_reminder_wishes/<int:pk>/<int:participant_id>",
        InvitationReminderWishesView.as_view(),
        name="send_reminder_wishes",
    ),
    path(
        "send_invitations_wait/<int:pk>/<str:task_ids>",
        InvitationWaitView.as_view(),
        name="send_invitations_wait",
    ),
    path(
        "send_invitations_wishes_wait/<int:pk>/<str:task_ids>",
        InvitationWishesWaitView.as_view(),
        name="send_invitations_wishes_wait",
    ),
    path(
        "event_list/",
        EventListView.as_view(),
        name="event_list",
    ),
    path(
        "status_stream/<int:pk>/<str:task_ids>",
        InvitationStreamWaitView.as_view(),
        name="event_send_invitation_status_stream",
    ),
    path(
        "status_stream_wishes/<int:pk>/<str:task_ids>",
        InvitationWishesStreamWaitView.as_view(),
        name="event_send_invitation_wishes_status_stream",
    ),
]
