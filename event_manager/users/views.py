from django.contrib.auth import authenticate
from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response

from events.models import EventAttendee
from users.jwt import JWTAuthentication
from users.models import User, UserToken
from users.permissions import IsSuperUser
from users.serializers import (CreateUpdateUserSerializer, GetUserSerializer,
                               UserLoginSerializer)
from django.contrib.auth.hashers import make_password


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().filter(is_deleted=False)
    serializer_class = CreateUpdateUserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return super().get_queryset()

    def get_permissions(self):
        if self.action == 'list':
            return [IsSuperUser()]
        return super().get_permissions()

    def retrieve(self, request, *args, **kwargs):
        user = self.request.user
        serializer = GetUserSerializer(user)
        upcoming_events = EventAttendee.objects.filter(user=user).values("event__id", "event__title",
                                                                         "event__location", "event__date",
                                                                         "event__time")
        response_data = serializer.data
        response_data["upcoming_events"] = list(upcoming_events)
        return Response(response_data)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = GetUserSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['password'] = make_password(request.data['password'])
        user = serializer.save()
        response_serializer = GetUserSerializer(user)
        return Response(response_serializer.data, status=201)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        user = self.request.user
        serializer = self.serializer_class(user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated_user = serializer.save()
        response_serializer = GetUserSerializer(updated_user)
        return Response(response_serializer.data)

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        user.soft_delete(user)
        return Response({"message": "User deleted successfully"}, status=200)


class UserLoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        user = User.objects.filter(email=email, is_deleted=False).first()
        if user and user.check_password(password):
            UserToken.objects.create(authToken=user.token, user=user.id)
            return Response({
                "user_id": user.id,
                "user": user.email,
                "mobile_number": user.mobile_number,
                "is_superuser": user.is_superuser,
                "token": user.token
            }, status=200)
        return Response({"message": "Invalid credentials, try again"}, status=401)
