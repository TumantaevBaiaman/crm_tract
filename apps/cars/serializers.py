from rest_framework import serializers

from . import models


class SerializerCar(serializers.ModelSerializer):

    class Meta:
        model = models.ModelsCars
        fields = "__all__"

