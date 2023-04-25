from datetime import datetime, timedelta
import json

import django
from django.contrib import messages
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.timezone import now

from events.models import Event, Participant
from users.models import User

from .forms import LoginForm, UserForm, EventForm, CreateEventForm

DEFAULT_PASSWORD = "defaultpassword"
PAGE_ITEMS_PER_PAGE = 1

from .forms import LoginForm, UserForm, EventForm, CreateEventForm

DEFAULT_PASSWORD = "defaultpassword"
PAGE_ITEMS_PER_PAGE = 5


@login_required
def home(request):
    template = 'pages/index.html'
    upcoming_events = Event.objects.filter(start_date__gte=timezone.now()).order_by('start_date')
    # Get the count of events and participants by month
    start_date = datetime.now() - timedelta(days=365)
    events_by_month = Event.objects.filter(start_date__gte=start_date).annotate(month=TruncMonth('start_date')).values(
        'month').annotate(count=Count('id'))
    participants_by_month = Participant.objects.filter(event__start_date__gte=start_date).annotate(
        month=TruncMonth('event__start_date')).values('month').annotate(count=Count('id'))

    # Convert the data to a list of tuples
    data = []
    months = set()
    for event_count in events_by_month:
        month = event_count['month'].strftime('%Y-%m')
        count = event_count['count']
        months.add(month)
        data.append((month, count, 0))
    for participant_count in participants_by_month:
        month = participant_count['month'].strftime('%Y-%m')
        count = participant_count['count']
        months.add(month)
        for i in range(len(data)):
            if data[i][0] == month:
                data[i] = (month, data[i][1], count)
                break
        else:
            data.append((month, 0, count))

    # Sort the data by month
    data.sort(key=lambda x: x[0])

    # Get the top 10 participants
    top_participants = Participant.objects.values('user__email', 'user__first_name', 'user__last_name').annotate(num_events=Count('event')).order_by('-num_events')[:10]
    top_events = Event.objects.annotate(num_participants=Count('participant')).order_by('-num_participants')[:10]

    context = {
        'data': data,
        'months': sorted(months),
        'upcoming_events': upcoming_events,
        'top_participants': top_participants,
        'top_events': top_events,
    }

    return render(request, template, context)


def register_user(request):
    template = 'pages/register_user.html'
    register_user_form = UserForm()
    context = {'register_user_form': register_user_form}
    # if request is a POST request, then save the user to the database
    if request.method == 'POST':
        register_user_form = UserForm(request.POST)


@login_required
def user_manage(request):
    template = 'pages/user/manage_user.html'
    users = User.objects.all()

    # if request is a POST request, get the list of users to be deleted and delete those events
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))['delete_list']
        if not data:
            messages.warning(request, 'No users selected.')
        else:
            for data_id in data:
                User.objects.get(pk=int(data_id)).delete()
            messages.success(request, 'Selected users deleted...')
        response = {'isSuccess': True, }
        return JsonResponse(response)

    # if request is a GET request, search for related columns using the search_val variable
    if request.method == "GET":
        search_val = request.GET.get('s', '')
        users = users.filter(Q(email__icontains=search_val))

        # Pagination for table
        paginator = Paginator(users, PAGE_ITEMS_PER_PAGE)
        page = request.GET.get('page')
        users = paginator.get_page(page)
    return render(request, template, {'users': users})


def register_user(request):
    template = 'pages/user/register_user.html'
    register_user_form = UserForm()
    context = {'register_user_form': register_user_form}
    # if request is a POST request, then save the user to the database
    if request.method == 'POST':
        register_user_form = UserForm(request.POST)
        if register_user_form.is_valid():
            email = register_user_form.cleaned_data['email']
            password = DEFAULT_PASSWORD
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


@login_required
def user_edit(request, user_id):
    template = 'pages/user/edit_user.html'
    user = get_object_or_404(User, pk=user_id)
    # Edit user details
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        if user_form.is_valid():
            user_form.save()
            messages.add_message(request, messages.SUCCESS, "User profile changes has been saved...")
            return redirect('user_manage')
    else:
        user_form = UserForm(instance=user)
    context = {"user_form": user_form, "user_id": user_id}
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


@login_required
def event_home(request):
    template = 'pages/event/index.html'
    user = request.user
    events = user.event_set.all()
    context = {
        'user': user,
        'events': events,
    }
    return render(request, template, context)


@login_required
def event_details(request, event_id):
    template = 'pages/event/event_details.html'
    event = Event.objects.get(pk=event_id)
    participants = event.participant_set.all()
    context = {
        "event": event,
        "participants": participants,
    }
    return render(request, template, context)


@login_required
def event_manage(request):
    template = 'pages/event/manage_event.html'
    events = Event.objects.all()

    # if request is a POST request, get the list of events to be deleted and delete those events
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))['delete_list']
        if not data:
            messages.warning(request, 'No events selected.')
        else:
            for data_id in data:
                Event.objects.get(pk=int(data_id)).delete()
            messages.success(request, 'Selected events deleted...')
        response = {'isSuccess': True, }
        return JsonResponse(response)

    # if request is a GET request, search for related columns using the search_val variable
    if request.method == "GET":
        search_val = request.GET.get('s', '')
        events = events.filter(Q(title__icontains=search_val))

        # Pagination for table
        paginator = Paginator(events, PAGE_ITEMS_PER_PAGE)
        page = request.GET.get('page')
        events = paginator.get_page(page)
    return render(request, template, {'events': events})




@login_required
def event_create(request):
    template = 'pages/event/create_event.html'
    create_event_form = CreateEventForm()
    context = {'create_event_form': create_event_form}
    # if request is a POST request, then save the event to the database
    if request.method == 'POST':
        create_event_form = CreateEventForm(request.POST)
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


@login_required
def event_edit(request, event_id):
    template = 'pages/event/edit_event.html'
    event = get_object_or_404(Event, pk=event_id)

    # edit event details
    if request.method == 'POST':
        event_form = EventForm(request.POST, instance=event)
        if event_form.is_valid():
            event_form.save()

            return redirect('event_manage')
    else:
        event_form = EventForm(instance=event)
    context = {"event_form": event_form, "event_id": event_id}
    return render(request, template, context)


@login_required
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
