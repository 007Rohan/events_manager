from django.urls import path

from users.views import UserLoginView, UserViewSet

app_name = "users"
trailing_slash = False

urlpatterns = [
    path("", UserViewSet.as_view({"get": "list", "post": "create", }), name="user-list"),
    path("update/", UserViewSet.as_view({"put": "update"}), name="user-detail"),
    path("delete/", UserViewSet.as_view({"delete": "destroy"}), name="user-detail"),
    path("info/", UserViewSet.as_view({"get": "retrieve"}), name="user-detail"),
    path("login/", UserLoginView.as_view(), name="user-login"),
]
