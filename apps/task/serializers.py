from rest_framework import serializers
from . import models


class SerializerTask(serializers.ModelSerializer):

    class Meta:
        model = models.ModelsTask
        fields = "__all__"
