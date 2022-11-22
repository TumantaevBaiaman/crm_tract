from rest_framework import serializers
from . import models
from apps.task.serializers import SerializerCreateTask


class SerializerCreateInvoice(serializers.ModelSerializer):

    class Meta:
        model = models.ModelsInvoice
        fields = "__all__"

