from django import forms
from django.forms import ModelForm
from django.utils import timezone

from events.models import Event
from users.models import User, ParticipantUser


class DateTimeInput(forms.DateInput):
    input_type = 'datetime-local'


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')


class UserForm(ModelForm):
    email = forms.EmailField(label='Email')
    first_name = forms.CharField(label='First Name')
    middle_name = forms.CharField(label='Middle Name')
    last_name = forms.CharField(label='Last Name')
    user_id = forms.CharField(label='User ID')

    class Meta:
        model = User
        fields = ('email', 'first_name', 'middle_name', 'last_name', 'user_id')
        widgets = {
            'is_admin': forms.CheckboxInput(attrs={'class': 'v_form_checkbox'})
        }


class ParticipantForm(ModelForm):
    email = forms.EmailField(label='Email')
    first_name = forms.CharField(label='First Name')
    middle_name = forms.CharField(label='Middle Name')
    last_name = forms.CharField(label='Last Name')
    user_id = forms.CharField(label='User ID')

    class Meta:
        model = ParticipantUser
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


class CreateEventForm(forms.ModelForm):
    organizer = forms.ModelChoiceField(queryset=User.objects.all().order_by('last_name'), initial='FIXED')
    start_date = forms.DateTimeField(
        input_formats=['%Y-%m-%d %H:%M:%S'],
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    )
    end_date = forms.DateTimeField(
        input_formats=['%Y-%m-%d %H:%M:%S'],
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    )

    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        if start_date <= timezone.now():
            raise forms.ValidationError("Start date and time must be in the future.")
        return start_date

    def clean_end_date(self):
        end_date = self.cleaned_data.get('end_date')
        start_date = self.cleaned_data.get('start_date')
        if end_date <= timezone.now():
            raise forms.ValidationError("End date and time must be in the future.")
        if start_date and end_date and end_date <= start_date:
            raise forms.ValidationError("End date and time must be after start date and time.")
        return end_date

    class Meta:
        model = Event
        fields = ['title', 'description', 'venue', 'start_date', 'end_date']
