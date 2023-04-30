from datetime import datetime
from django.db import models
from users.models import User, ParticipantUser


class Event(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    venue = models.CharField(max_length=100, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Participant(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    participant_user = models.ForeignKey(ParticipantUser, on_delete=models.CASCADE)
    scan_in = models.DateTimeField(default=datetime.now, blank=True)
    scan_out = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return str(self.event)+' - '+str(self.participant_user)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['event', 'participant_user'], name='unique_event_participant'
            )
        ]


class Setting(models.Model):
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=250)
