from rest_framework import serializers
from . import models


class SerializerInvoice(serializers.ModelSerializer):

    class Meta:
        model = models.ModelsInvoice
        fields = "__all__"

