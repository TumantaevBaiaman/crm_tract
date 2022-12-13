from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import (
    ModelsUser, ModelsSatus, ModelsAccount
)


def serialize_errors(serializer_errors):
    errors = []
    for field_name, field_errors in serializer_errors.items():
        for field_error in field_errors:
            errors.append(field_error)
    return errors


class SerializerSatus(serializers.ModelSerializer):

    class Meta:
        model = ModelsSatus
        fields = "__all__"


class SerializerUser(serializers.ModelSerializer):

    class Meta:
        model = ModelsUser
        fields = (
            'id',
            'email',
            'username',
            'lastname',
            "date_of_birth"
        )


class SerializerRegisterAccount(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=ModelsUser.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = ModelsUser
        fields = (
            'email',
            'password',
            'username',
            'lastname',
            'date_of_birth',
            'status',
            'phone'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value: str):
        return make_password(value)


class SerializerRegisterUser(serializers.Serializer):
    account_id = serializers.SlugRelatedField(many=False, slug_field='id', queryset=ModelsAccount.objects.all())
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=ModelsUser.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    lastname = serializers.CharField(write_only=True, required=True)
    phone = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = ModelsUser
        fields = (
            'account_id',
            'email',
            'password',
            'username',
            'lastname',
            'date_of_birth',
            'status',
            'phone'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value: str):
        return make_password(value)


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    def validate_password(self, value: str) -> str:
        """Validate whether the password meets all django validator requirements."""
        validate_password(value)
        return value