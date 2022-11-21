from rest_framework import serializers
from . import models


class SerializerCreateAccount(serializers.ModelSerializer):

    class Meta:
        model = models.ModelsAccount
        fields = (
            'name',
            'status'
        )