from django import forms

from users.models import User


class DateTimeInput(forms.DateInput):
    input_type = 'datetime-local'


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')


class RegisterUserForm(forms.Form):
    email = forms.EmailField(label='Email')
    first_name = forms.CharField(label='First Name')
    middle_name = forms.CharField(label='Middle Name')
    last_name = forms.CharField(label='Last Name')
    user_id = forms.CharField(label='User ID')


class CreateEventForm(forms.Form):
    title = forms.CharField(label='Title')
    description = forms.CharField(label='Description')
    venue = forms.CharField(label='Venue')
    start_date = forms.DateTimeField(label='Start Date', widget=DateTimeInput)
    end_date = forms.DateTimeField(label='End Date', widget=DateTimeInput)
    organizer = forms.ModelChoiceField(queryset=User.objects.all().order_by('last_name'), initial='FIXED')
