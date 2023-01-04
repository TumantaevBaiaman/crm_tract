from rest_framework import serializers
from . import models
from ..cars.serializers import SerializerCar
from ..customer.serializers import SerializerCustomer
from ..task.serializers import SerializerTask
from ..users.serializers import SerializerUser


class SerializerInvoice(serializers.ModelSerializer):
    car_id = SerializerCar(read_only=True)
    customer_id = SerializerCustomer(read_only=True)
    crew_id = SerializerUser(read_only=True)
    tasks = SerializerTask(many=True, read_only=True)

    class Meta:
        model = models.ModelsInvoice
        fields = "__all__"

