from celery import shared_task

from .models import EventAttendee


@shared_task(bind=True)
def book_event_task(self, event_id, user_id):
    EventAttendee.objects.create(event_id=event_id, user_id=user_id)
    return {"message": "Event successfully booked", "event_id": event_id, "user_id": user_id}
