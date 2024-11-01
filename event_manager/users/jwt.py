import jwt
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import exceptions
from rest_framework.authentication import (BaseAuthentication,
                                           get_authorization_header)

from .models import User, UserToken


class JWTAuthentication(BaseAuthentication):

    def authenticate(self, request):

        auth_header = get_authorization_header(request)

        auth_data = auth_header.decode("utf-8")

        authToken = auth_data.split(" ")

        if len(authToken) != 2:
            raise exceptions.AuthenticationFailed("Token not valid")

        token = authToken[1]

        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms="HS256")

            id = payload["id"]
            email = payload["email"]

            user = User.objects.get(id=id, email=email)
            userTok = UserToken.objects.filter(authToken=token, user=user.id).first()
            if userTok is None:
                raise exceptions.AuthenticationFailed(
                    "Token is expired, login again"
                )
            return (user, token)

        except jwt.ExpiredSignatureError as ex:
            raise exceptions.AuthenticationFailed(
                "Token is expired, login again")

        except jwt.DecodeError as ex:
            raise exceptions.AuthenticationFailed(
                "Token is invalid,")

        except ObjectDoesNotExist as no_user:
            raise exceptions.AuthenticationFailed(
                "Token invalid")

        return super().authenticate(request)
