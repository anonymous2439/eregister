from django.contrib import admin
from events.models import Event, Participant, Setting

admin.site.register(Event)
admin.site.register(Participant)
admin.site.register(Setting)
