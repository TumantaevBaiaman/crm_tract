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

    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    status = models.ForeignKey(
        ModelsSatus, on_delete=models.CASCADE,
        null=True, blank=True
    )
    username = models.CharField(max_length=255, blank=True, null=True)
    lastname = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(
        default=datetime.now, blank=True, null=True
    )
    phone = models.CharField(max_length=20, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ()

    objects = CustomUserManager()

    @staticmethod
    def has_perm(perm, obj=None):
        # "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    @staticmethod
    def has_module_perms(app_label):
        # "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    def __str__(self):
        return f"{self.id}: {self.email}"


