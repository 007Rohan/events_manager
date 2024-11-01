from django.db import IntegrityError
from rest_framework import serializers

from .models import Event, EventAttendee


class CreateUpdateEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"


class GetEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "title", "location", "date", "time"]


class GetEventInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fieldss = ["title", "location", "date", "time"]


class EventAttendeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventAttendee
        fields = ["event"]

    def validate_event(self, value):
        if not Event.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Event does not exist.")
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        event = attrs.get("event")
        if EventAttendee.objects.filter(user=user, event=event.id).exists():
            raise serializers.ValidationError("User is already attending this event.")

        booked_events = EventAttendee.objects.filter(user=user).select_related('event')

        for booking in booked_events:
            if (booking.event.date == event.date and booking.event.time == event.time):
                raise serializers.ValidationError("Event timing conflicts with another event the user is attending.")
        return attrs

    def create(self, validated_data):
        event_attendee = EventAttendee.objects.create(**validated_data)
        return event_attendee
