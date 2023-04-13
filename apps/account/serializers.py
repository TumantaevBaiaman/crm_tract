from rest_framework import serializers
from . import models


class ModelsStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ModelsSatusAccount
        fields = '__all__'


class SerializerAccount(serializers.ModelSerializer):
    status = ModelsStatusSerializer(read_only=True)

    class Meta:
        model = models.ModelsAccount
        fields = '__all__'

