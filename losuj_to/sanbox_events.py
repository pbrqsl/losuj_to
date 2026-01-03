from events.models import Event, Exclusion, Participant
from django.test.utils import CaptureQueriesContext
from django.db import connection

events = Event.objects.all()
for e in events:
    print(e.event_name)
    print(e.id)
    

event_id = 2
excludes = {}



with CaptureQueriesContext(connection) as ctx:
    excludes_queryset = Exclusion.objects.filter(event_id=event_id)
    for exclude in excludes_queryset:
        if exclude.participant.user.email not in excludes:  
            excludes[exclude.participant.user.email] = [
                exclude.excluded_participant.user.email
            ]



print("Excludes::")
print(excludes)
print(f"ilosc zapytan: {len(ctx)}")

event_id = 2
with CaptureQueriesContext(connection) as ctx2:
    excludes_queryset = Exclusion.objects.filter(event_id=event_id).select_related(
        'participant__user', 'excluded_participant__user'
    )
    for exclude in excludes_queryset:
        if exclude.participant.user.email not in excludes:  
            excludes[exclude.participant.user.email] = [
                exclude.excluded_participant.user.email
                ]

print("Excludes::")
print(excludes)
print(f"ilosc zapytan: {len(ctx2)}")

# participants = []

# participants_queryset = Participant.objects.filter(event_id=event_id)
# for participant_item in participants_queryset:
#     participants.append([participant_item.user.email, participant_item.name])

# excludes_queryset = Exclusion.objects.filter(event_id=event_id)

# for exclude in excludes_queryset:
#     if exclude.participant.user.email not in excludes:
#         excludes[exclude.participant.user.email] = [
#             exclude.excluded_participant.user.email
#         ]
#     else:
#         excludes[exclude.participant.user.email].append(
#             exclude.excluded_participant.user.email
#         )