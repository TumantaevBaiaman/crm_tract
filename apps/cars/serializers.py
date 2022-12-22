from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from . import models
from ..users.models import ModelsUser
from apps.users.serializers import (
    SerializerUser
)


class SerializerCar(serializers.ModelSerializer):

    class Meta:
        model = models.ModelsCars
        fields = "__all__"

