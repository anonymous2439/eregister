from django.contrib import admin

from events.models import Event

from events.models import Participant

admin.site.register(Event)
admin.site.register(Participant)