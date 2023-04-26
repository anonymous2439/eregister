from django.contrib import admin
from .models import User, ParticipantUser

admin.site.register(User)
admin.site.register(ParticipantUser)