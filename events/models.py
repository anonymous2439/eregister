from datetime import datetime

from django.db import models
from django.utils import timezone

from users.models import User


class Event(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    venue = models.CharField(max_length=100, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)


class Participant(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_participated = models.DateTimeField(default=datetime.now, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['event', 'user'], name='unique_event_user'
            )
        ]
