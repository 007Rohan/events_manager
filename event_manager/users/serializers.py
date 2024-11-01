from rest_framework import serializers

from .models import User


class CreateUpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "mobile_number"]


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ("email", "password", "token")

        read_only_fields = ["token"]

    def validate_email(self, value):
        if not User.objects.filter(email=value, is_deleted=False).exists():
            raise serializers.ValidationError("No account found with this email address.")
        return value
