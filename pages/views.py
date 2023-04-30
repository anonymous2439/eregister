import csv
from datetime import datetime, timedelta
import json

import django
from django.contrib import messages
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from events.models import Event, Participant
from users.models import User, ParticipantUser

from .forms import LoginForm, UserForm, EventForm, CreateEventForm, ParticipantForm, ParticipantUserForm, SettingForm

DEFAULT_PASSWORD = "defaultpassword"
PAGE_ITEMS_PER_PAGE = 1


@login_required
def home(request):
    template = 'pages/dashboard.html'
    if request.user.is_superuser:
        upcoming_events = Event.objects.filter(start_date__gte=timezone.now()).order_by('start_date')
    else:
        upcoming_events = Event.objects.filter(start_date__gte=timezone.now(), organizer=request.user).order_by('start_date')
    # Get the count of events and participants by month
    start_date = datetime.now() - timedelta(days=365)
    if request.user.is_superuser:
        events_by_month = Event.objects.filter(start_date__gte=start_date).annotate(
            month=TruncMonth('start_date')).values(
            'month').annotate(count=Count('id'))
        participants_by_month = Participant.objects.filter(event__start_date__gte=start_date).annotate(
            month=TruncMonth('event__start_date')).values('month').annotate(count=Count('id'))
    else:
        events_by_month = Event.objects.filter(start_date__gte=start_date, organizer=request.user.is_superuser).annotate(
            month=TruncMonth('start_date')).values(
            'month').annotate(count=Count('id'))
        participants_by_month = Participant.objects.filter(event__start_date__gte=start_date, event__organizer=request.user.is_superuser).annotate(
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
    top_participants = Participant.objects.values('participant_user__email', 'participant_user__first_name', 'participant_user__last_name').annotate(num_events=Count('event')).order_by('-num_events')[:10]
    top_events = Event.objects.annotate(num_participants=Count('participant')).order_by('-num_participants')[:10]

    context = {
        'data': data,
        'months': sorted(months),
        'upcoming_events': upcoming_events,
        'top_participants': top_participants,
        'top_events': top_events,
    }

    return render(request, template, context)


@login_required
def profile(request, user_id):
    template = 'pages/user/profile.html'
    user = User.objects.get(pk=user_id)
    context = { 'user': user }
    return render(request, template, context)


@login_required
def reset_password(request, user_id):
    messages.success(request, 'Password reset successfully!')
    return redirect('profile', user_id=user_id)


def set_default_password(request):
    messages.success(request, 'Default Password is Set!')
    return redirect('organizer_manage')


@login_required
def organizer_manage(request):
    template = 'pages/user/manage_organizer.html'
    users = User.objects.all()
    setting_form = SettingForm()

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
    return render(request, template, {'users': users, 'setting_form': setting_form,})


@login_required
def participant_manage(request):
    template = 'pages/user/manage_participant.html'
    participant_users = ParticipantUser.objects.all()

    # if request is a POST request, get the list of users to be deleted and delete those events
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))['delete_list']
        if not data:
            messages.warning(request, 'No participants selected.')
        else:
            for data_id in data:
                ParticipantUser.objects.get(pk=int(data_id)).delete()
            messages.success(request, 'Selected users deleted...')
        response = {'isSuccess': True, }
        return JsonResponse(response)

    # if request is a GET request, search for related columns using the search_val variable
    if request.method == "GET":
        search_val = request.GET.get('s', '')
        participant_users = participant_users.filter(Q(email__icontains=search_val))

        # Pagination for table
        paginator = Paginator(participant_users, PAGE_ITEMS_PER_PAGE)
        page = request.GET.get('page')
        participant_users = paginator.get_page(page)
    return render(request, template, {'participant_users': participant_users})


def register_organizer(request):
    template = 'pages/user/register_organizer.html'
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


def register_participant(request):
    template = 'pages/user/register_participant.html'
    register_participant_form = ParticipantForm()
    context = {'register_participant_form': register_participant_form}
    # if request is a POST request, then save the user to the database
    if request.method == 'POST':
        register_user_form = UserForm(request.POST)
        if register_user_form.is_valid():
            email = register_user_form.cleaned_data['email']
            first_name = register_user_form.cleaned_data['first_name']
            middle_name = register_user_form.cleaned_data['middle_name']
            last_name = register_user_form.cleaned_data['last_name']
            user_id = register_user_form.cleaned_data['user_id']
            participant_user = ParticipantUser(email=email, first_name=first_name, middle_name=middle_name, last_name=last_name, user_id=user_id)
            participant_user.save()
            if participant_user is not None:
                messages.add_message(request, messages.SUCCESS, "Participant successfully registered")
            else:
                messages.add_message(request, messages.ERROR, "An error occurred while trying to save the participant record...")
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
            return redirect('organizer_manage')
    else:
        user_form = UserForm(instance=user)
    context = {"user_form": user_form, "user_id": user_id}
    return render(request, template, context)


def participant_user_edit(request, user_id):
    template = 'pages/user/edit_participant.html'
    user = get_object_or_404(ParticipantUser, pk=user_id)
    # Edit user details
    if request.method == 'POST':
        user_form = ParticipantUserForm(request.POST, instance=user)
        if user_form.is_valid():
            user_form.save()
            messages.add_message(request, messages.SUCCESS, "User profile changes has been saved...")
            return redirect('participant_manage')
    else:
        user_form = ParticipantUserForm(instance=user)
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
    today = datetime.now()
    context = {
        'user': user,
        'events': events,
        'today': today,
    }
    return render(request, template, context)


@login_required
def event_details(request, event_id):
    template = 'pages/event/event_details.html'
    event = Event.objects.get(pk=event_id)
    participants = event.participant_set.all()
    today = datetime.now()
    context = {
        "event": event,
        "participants": participants,
        "today": today,
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
        participant_user = ParticipantUser.objects.get(user_id=data['user_id'])
        event = Event.objects.get(pk=data['event_id'])
        participant = Participant(participant_user=participant_user, event=event)
        try:
            participant.save()
        except django.db.utils.IntegrityError:
            participant = Participant.objects.get(participant_user=participant_user, event=event)
            participant.scan_out = datetime.now()
            participant.save()
        response = {
            'participant_firstname': participant.participant_user.first_name,
            'participant_lastname': participant.participant_user.last_name,
            'participant_participated': participant.scan_in.strftime("%c"),
            'message': "Thank you for joining the event!",
            'isSuccess': True,
        }
        return JsonResponse(response)
    return render(request, template, context)


def generate_csv(request, event_id):
    event = Event.objects.get(pk=event_id)
    participants = event.participant_set.all()

    # Get data to write to CSV
    data = [
        ['User ID', 'Email', 'First Name', 'Middle Name', 'Last Name', 'In', 'Out'],
    ]

    for participant in participants:
        user = participant.participant_user
        data.append([user.user_id, user.email, user.first_name, user.middle_name, user.last_name, participant.scan_in, participant.scan_out])

    # Create a response object with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="data.csv"'

    # Create a CSV writer object
    writer = csv.writer(response)

    # Write data to CSV
    for row in data:
        writer.writerow(row)

    return response


def send_survey(request, event_id):
    event = Event.objects.get(pk=event_id)
    participants = event.participant_set.all()

    subject = 'Eregister Survey'
    # Render the HTML template and convert it to plain text
    html_message = render_to_string('survey_email.html')
    plain_message = strip_tags(html_message)
    from_email = 'eregister@gmail.com'
    to_emails = [participant.participant_user.email for participant in participants]

    # Create the EmailMultiAlternatives object to send both HTML and plain text versions of the email
    email = EmailMultiAlternatives(subject, plain_message, from_email, to_emails)
    email.attach_alternative(html_message, "text/html")
    email.send()
    return redirect('event_details', event_id=event_id)
