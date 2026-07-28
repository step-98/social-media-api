import os
import uuid

from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.db import models
from django.utils.translation import gettext as _
from datetime import date


class UserManager(DjangoUserManager):

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


def avatar_path(instance: "User", filename: str) -> str:
    _, ext = os.path.splitext(filename)
    return os.path.join(
        "uploads/avatars/",
        f"{instance.pk}-{uuid.uuid4()}{ext}"
    )

class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    bio = models.TextField(_("Bio"), blank=True)
    avatar = models.ImageField(upload_to=avatar_path, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - (
        (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()
