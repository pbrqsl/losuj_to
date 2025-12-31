from events.models import Event, Exclusion, Participant


events = Event.objects.all()
for e in events:
    print(e.event_name)
    print(e.id)
    

event_id = 2
excludes = {}

excludes_queryset = Exclusion.objects.filter(event_id=event_id)
for exclude in excludes_queryset:
    if exclude.participant.user.email not in excludes:  
        excludes[exclude.participant.user.email] = [
            exclude.excluded_participant.user.email
        ]

print("Excludes::")
print(excludes)

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