import uuid

from django.db import models

from users.models import AbstractMixinModel, User


class Event(AbstractMixinModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    capacity = models.PositiveIntegerField()
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="event_created_by",
        null=True,
        blank=True,
    )
    modified_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="event_modified_by",
        null=True,
        blank=True,
    )
    deleted_by = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="event_deleted_by",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.title


class EventAttendee(AbstractMixinModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_attendees')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendees')
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="event_attendee_created_by",
        null=True,
        blank=True,
    )
    modified_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="event_attendee_modified_by",
        null=True,
        blank=True,
    )
    deleted_by = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="event_attendee_deleted_by",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.user} - {self.event}"
