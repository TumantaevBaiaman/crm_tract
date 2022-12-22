from rest_framework import serializers
from . import models


class SerializerAccount(serializers.ModelSerializer):
    class Meta:
        model = models.ModelsAccount
        fields = '__all__'

