import random

from django.shortcuts import get_object_or_404
from events.models import Draw, Participant


def event_draw(drawing_dict, participants):
    counter = 0
    while counter < 100:
        counter += 1
        drawn_participants = []
        draw_result = {}
        for participant in participants:
            drawing_pool = [
                x for x in drawing_dict[participant[0]] if x not in drawn_participants
            ]
            # to lambda
            if len(drawing_pool) == 0:
                continue
            drawn_participant = random.choice(drawing_pool)
            drawn_participants.append(drawn_participant)
            draw_result[participant[0]] = drawn_participant

        if len(draw_result) == len(participants):
            break
    return draw_result


def perform_drawing(event, participants, drawing_dict):
    draw_result = event_draw(drawing_dict=drawing_dict, participants=participants)
    print(draw_result)
    for key in draw_result:
        participant = get_object_or_404(Participant, user__email=key, event=event)
        drawn_participant = get_object_or_404(
            Participant, user__email=draw_result[key], event=event
        )
        Draw.objects.create(
            participant=participant,
            drawn_participant=drawn_participant,
            event=event,
        )
