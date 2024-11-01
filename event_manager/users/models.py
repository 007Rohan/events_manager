import uuid
from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

phone_regex = RegexValidator(
    regex=r"^\+?1?\d{8,15}$",
    message=_(
        "Phone number must be entered in the format: '+99999999' Up to 15 digits allowed."
    ),
)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, mobile_number, password, **extra_fields):
        # Creates and saves a User with the given email or mobile and password.
        if not (email or mobile_number):
            raise ValueError("Users must have either an email address or a mobile number")
        email = self.normalize_email(email)
        user = self.model(email=email, mobile_number=mobile_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

    def create_user(self, email, mobile_number, password=None, **extra_fields):
        # Create User method called at user registration.
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, mobile_number, password, **extra_fields)

    def create_superuser(self, email, mobile_number, password, **extra_fields):
        # Create superuser method called at superuser creation.
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, mobile_number, password, **extra_fields)


class AbstractMixinModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self, user):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save()


class User(AbstractMixinModel, AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=254, unique=True)
    mobile_number = models.CharField(max_length=15, validators=[phone_regex], null=True, blank=True)
    date_joined = models.DateField(null=True, blank=True, auto_now_add=True)
    is_admin_user = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_mobile_number_verified = models.BooleanField(default=False)

    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="user_created_by",
        null=True,
        blank=True,
    )
    modified_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="user_modified_by",
        null=True,
        blank=True,
    )
    deleted_by = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="user_deleted_by",
        null=True,
        blank=True,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["mobile_number"]

    @property
    def token(self):
        token = jwt.encode(
            {"id": self.id.hex,
             "email": self.email,
             "mobile_number": self.mobile_number,
             "exp": datetime.now() + timedelta(hours=24)},
            settings.SECRET_KEY, algorithm="HS256")

        return token

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.email


class UserToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.CharField(max_length=255, null=True, blank=True)
    authToken = models.CharField(max_length=256, null=True, blank=True)

    class Meta:
        db_table = "users_token"
