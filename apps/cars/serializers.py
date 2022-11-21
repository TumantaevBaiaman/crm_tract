from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import (
    ModelsCars
)
from ..users.models import ModelsUser
from apps.users.serializers import (
    SerializerUser
)


class SerializerCar(serializers.ModelSerializer):
    customer = SerializerUser()

    class Meta:
        model = ModelsCars
        fields = (
            'customer',
            'description',
            'vin',
            'model',
            'image',
            'create_at'
        )


class SerializerCreateCar(serializers.Serializer):

    class Meta:
        model = ModelsCars
        fields = [
            'customer',
            'description',
            'vin',
            'model',
            'image'
        ]
        read_only = ['customer']

    # def create(self, validated_data):
    #     info_user = ModelsUser.objects.get(validated_data['customer'])
    #     if info_user.status=='customer' or info_user.is_admin==True:
    #         car = ModelsCars(
    #             customer_id=validated_data['']
    #         )
    #         car.save()
