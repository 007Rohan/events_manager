from celery.result import AsyncResult
from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response

import users.models
from users.jwt import JWTAuthentication
from users.permissions import IsSuperUser

from .celery_tasks import book_event_task
from .models import Event, EventAttendee
from .serializers import (CreateUpdateEventSerializer, EventAttendeeSerializer,
                          GetEventSerializer)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().filter(is_deleted=False)
    serializer_class = CreateUpdateEventSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSuperUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        location = self.request.query_params.get("location", None)
        date = self.request.query_params.get("date", None)
        filter_criteria = Q()
        if location:
            filter_criteria &= Q(location__iexact=location)
        if date:
            try:
                date_obj = timezone.datetime.strptime(date, "%Y-%m-%d").date()
                filter_criteria &= Q(date=date_obj)
            except Exception as e:
                print(f"Raising Exception {e}")
                pass
        return queryset.filter(filter_criteria)

    def retrieve(self, request, *args, **kwargs):
        event = self.get_object()
        serializer = GetEventSerializer(event)
        booked_users = EventAttendee.objects.filter(event=event).values("user__id", "user__email",
                                                                        "user__mobile_number")
        response_data = serializer.data
        response_data["booked_users"] = list(booked_users)
        return Response(response_data)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = GetEventSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = serializer.save()
        response_serializer = GetEventSerializer(event)
        return Response(response_serializer.data, status=201)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        event = self.get_object()
        serializer = self.serializer_class(event, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated_event = serializer.save()
        response_serializer = GetEventSerializer(updated_event)
        return Response(response_serializer.data)

    def destroy(self, request, *args, **kwargs):
        event = self.get_object()
        event.soft_delete(request.user)
        return Response({"message": "Event deleted successfully"}, status=200)


class BookEvent(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.AllowAny]
    serializer_class = EventAttendeeSerializer

    def get(self, request):
        task_id = request.data["task_id"]
        result = AsyncResult(task_id)
        if result.state == "PROGRESS":
            response = {"status": "PROGRESS", "current": result.info.get("current", 0),
                        "total": result.info.get("total", 1)}
        elif result.state == "SUCCESS":
            response = {"status": "SUCCESS", "result": result.result}
        elif result.state == "FAILURE":
            response = {"status": "FAILURE", "error": str(result.result)}
        else:
            response = {"status": result.state}
        return Response(response)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        event_id = validated_data["event"].id
        user_id = request.user.id
        if not Event.objects.filter(id=event_id, is_deleted=False).exists():
            return Response({"status": "FAILED", "message": "This event does not exist"})
        task = book_event_task.delay(event_id, user_id)
        return Response({"status": "PROGESS", "task_id": task.id}, status=201)

    def destroy(self, request, *args, **kwargs):
        event = self.get_object()
        event.soft_delete(request.user)
        return Response({"message": "Booked Event removed successfully"}, status=200)
