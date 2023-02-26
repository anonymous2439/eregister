from django import forms
from django.forms import ModelForm

from events.models import Event
from users.models import User


class DateTimeInput(forms.DateInput):
    input_type = 'datetime-local'


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')


class RegisterUserForm(ModelForm):
    email = forms.EmailField(label='Email')
    first_name = forms.CharField(label='First Name')
    middle_name = forms.CharField(label='Middle Name')
    last_name = forms.CharField(label='Last Name')
    user_id = forms.CharField(label='User ID')

    class Meta:
        model = User
        fields = ('email', 'first_name', 'middle_name', 'last_name', 'user_id')


class EventForm(ModelForm):
    organizer = forms.ModelChoiceField(queryset=User.objects.all().order_by('last_name'), initial='FIXED')

    class Meta:
        model = Event
        fields = '__all__'
        widgets = {
            'start_date': forms.widgets.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.widgets.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
