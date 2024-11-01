from django.urls import include, path
from rest_framework import routers

from events.views import BookEvent, EventViewSet

app_name = "events"
trailing_slash = False

urlpatterns = [
    path("", EventViewSet.as_view({"get": "list", "post": "create", }), name="event-list"),
    path("<uuid:pk>/", EventViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"}),
         name="event-detail"),
    path("book/", BookEvent.as_view(), name="book-event"),
]
