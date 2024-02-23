from django.shortcuts import get_list_or_404, get_object_or_404

from .models import Event, Exclusion, Participant


def get_event_by_pk(event_id):
    return get_object_or_404(Event, id=event_id)


def get_and_validate_event(event: Event):
    is_valid = True
    participants_queryset = get_list_or_404(Participant, event=event)
    # excludes_queryset = get_list_or_404(Exclusion, event=event)
    excludes_queryset = Exclusion.objects.filter(event=event)

    errors = []
    participants = []
    excludes = {}

    validation_result = {
        "is_valid": is_valid,
        "participants": participants,
        "excludes": excludes,
        "errors": errors,
    }

    for participant in participants_queryset:
        participants.append([participant.user.email, participant.name])

    if excludes_queryset and len(participants_queryset) < 4:
        errors += (
            "The number of participants is currently to low to use exclude list. Please add participants to make excludes valid again.",
        )
        validation_result["is_valid"] = False
        print(validation_result["is_valid"])
        print("aaaaaaaaaaaaaaaaaaaaaaaaaa!!!!!!!!!!!!!!!!!!!!!!!")
        return validation_result

    else:
        excludes = {}
        for exclude in excludes_queryset:
            if exclude.participant.name not in excludes:
                excludes[exclude.participant.name] = []
            excludes[exclude.participant.name].append(exclude.excluded_participant.name)

    drawing_pools = []
    drawing_dict = {}
    for participant in participants_queryset:
        event_id = event.id
        participant_excludes = Exclusion.objects.filter(
            participant_id=participant.id
        ).filter(event_id=event_id)
        if not participant_excludes:
            exclude_pool = []
        else:
            exclude_pool = [
                exclude.excluded_participant for exclude in participant_excludes
            ]

        drawing_pool = [
            candidate.user.email
            for candidate in participants_queryset
            if candidate != participant and candidate not in exclude_pool
        ]
        drawing_pools.append(drawing_pool)
        drawing_dict[participant.user.email] = drawing_pool
        if len(drawing_pool) < 2:
            errors += (
                f"Exlusions for participant {participant} are to strict. Drawing names is not possible!",
            )
            validation_result["is_valid"] = False

    validation_result["excludes"] = excludes
    validation_result["drawing_dict"] = drawing_dict

    for drawing_pool in drawing_pools:
        if drawing_pools.count(drawing_pool) > len(drawing_pool):
            errors += ("Exlusions settings are to strict!",)
            validation_result["is_valid"] = False
            break

    return validation_result
