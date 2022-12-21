from rest_framework import serializers
from . import models


class SerializerCustomer(serializers.ModelSerializer):

    class Meta:
        model = models.ModelsCustomer
        fields = "__all__"


