from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import CustomUserManager
from datetime import datetime
from django.contrib.auth.models import PermissionsMixin

from ..account.models import ModelsAccount


class ModelsSatus(models.Model):
    name = models.CharField(max_length=55)
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ModelsUser(AbstractBaseUser, PermissionsMixin):
    account_id = models.ForeignKey(
        ModelsAccount, on_delete=models.CASCADE,
        null=True, blank=True
    )
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    is_staff = models.BooleanField(default=False)
    status = models.ForeignKey(
        ModelsSatus, on_delete=models.CASCADE,
        null=True, blank=True
    )
    username = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    date_of_birth = models.DateField(
        default=datetime.now, blank=True
    )
    phone = models.CharField(max_length=20)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ()

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.id}: {self.email}"


