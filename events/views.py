import json

from django.http import JsonResponse
from django.shortcuts import render

from users.models import User, ParticipantUser

from events.models import Participant, Event


def index(request):
    template = 'events/index.html'
    events = request.user.event_set.all()
    context = {
        "events": events
    }

    return render(request, template, context)


def read_qr(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        print(data)
        participant_user = ParticipantUser.objects.get(user_id=data['user_id'])
        event = Event.objects.get(pk=data['event_id'])
        participant = Participant(participant_user=participant_user, event=event).save()
        # print(user)
        response = {
            'id': participant_user.user_id,
            'email': participant_user.email,
        }
        return JsonResponse({"message": "success", "data": response})

    return JsonResponse({"message": "error"})
