import json

import django
from django.contrib import messages
from django.contrib.auth import authenticate, logout, login
from django.http import JsonResponse
from django.shortcuts import render, redirect
from events.models import Event, Participant
from users.models import User
from .forms import LoginForm, RegisterUserForm, EventForm

default_password = "defaultpassword"


def home(request):
    template = 'pages/index.html'

    return render(request, template)


def register_user(request):
    template = 'pages/register_user.html'
    register_user_form = RegisterUserForm()
    context = {'register_user_form': register_user_form}
    # if request is a POST request, then save the user to the database
    if request.method == 'POST':
        register_user_form = RegisterUserForm(request.POST)
        if register_user_form.is_valid():
            email = register_user_form.cleaned_data['email']
            password = default_password
            first_name = register_user_form.cleaned_data['first_name']
            middle_name = register_user_form.cleaned_data['middle_name']
            last_name = register_user_form.cleaned_data['last_name']
            user_id = register_user_form.cleaned_data['user_id']
            user = User(email=email, first_name=first_name, middle_name=middle_name, last_name=last_name, user_id=user_id)
            user.set_password(password)
            user.save()
            if user is not None:
                messages.add_message(request, messages.SUCCESS, "User successfully registered")
            else:
                messages.add_message(request, messages.ERROR, "An error occurred while trying to save the user record...")
    return render(request, template, context)


def login_view(request):
    template = 'pages/login.html'
    context = {'LoginForm': LoginForm}
    # if request is a POST request, perform the login process
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            email = login_form.cleaned_data['email']
            password = login_form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.add_message(request, messages.SUCCESS, 'Welcome '+str(user.first_name))
                return redirect('home')
            else:
                messages.add_message(request, messages.ERROR, 'Incorrect email / password')

    return render(request, template, context)


def logout_user(request):
    logout(request)
    return redirect('home')


def event_home(request):
    template = 'pages/event/index.html'
    user = request.user
    events = user.event_set.all()
    context = {
        'user': user,
        'events': events,
    }
    return render(request, template, context)


def event_details(request, event_id):
    template = 'pages/event/event_details.html'
    event = Event.objects.get(pk=event_id)
    participants = event.participant_set.all()
    for participant in participants:
        print(participant.user.first_name)
    context = {
        "event": event,
        "participants": participants,
    }
    return render(request, template, context)


def event_manage(request):
    template = 'pages/event/manage_event.html'
    events = Event.objects.all()
    # if request is a POST request, get the list of events to be deleted and delete those events
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))['delete_list']

        for data_id in data:
            Event.objects.get(pk=int(data_id)).delete()
        messages.add_message(request, messages.SUCCESS, 'Selected events deleted...')
        response = {'isSuccess': True, }
        return JsonResponse(response)
    return render(request, template, {"events": events})


def event_create(request):
    template = 'pages/event/create_event.html'
    create_event_form = EventForm()
    context = {'create_event_form': create_event_form}
    # if request is a POST request, then save the event to the database
    if request.method == 'POST':
        create_event_form = EventForm(request.POST)
        if create_event_form.is_valid():
            title = create_event_form.cleaned_data['title']
            description = create_event_form.cleaned_data['description']
            venue = create_event_form.cleaned_data['venue']
            start_date = create_event_form.cleaned_data['start_date']
            end_date = create_event_form.cleaned_data['end_date']
            organizer = create_event_form.cleaned_data['organizer']
            event = Event(title=title, description=description, venue=venue, start_date=start_date, end_date=end_date, organizer=organizer)
            event.save()
            if event is not None:
                messages.add_message(request, messages.SUCCESS, 'Event successfully created')
            else:
                messages.add_message(request, messages.ERROR, 'An error occurred while trying to create the event')

    return render(request, template, context)


def event_edit(request, event_id):
    template = 'pages/event/edit_event.html'
    event_form = EventForm(instance=Event.objects.get(pk=event_id))
    context = {"event_form": event_form}
    return render(request, template, context)


def event_participate(request, event_id):
    template = "pages/event/participate.html"
    event = Event.objects.get(pk=event_id)
    context = {
        'event': event,
    }
    # if request is a POST request, then get the info of the participant and the event and save it to the database
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        user = User.objects.get(user_id=data['user_id'])
        event = Event.objects.get(pk=data['event_id'])
        try:
            participant = Participant(user=user, event=event)
            participant.save()
            response = {
                'participant_firstname': participant.user.first_name,
                'participant_lastname': participant.user.last_name,
                'participant_participated': participant.date_participated.strftime("%c"),
                'message': "Thank you for joining the event!",
                'isSuccess': True,
            }
        except django.db.utils.IntegrityError:
            response = {'message': "User has already participated in this event", 'isSuccess': False, }

        return JsonResponse(response)
    return render(request, template, context)
