from rest_framework import status
from rest_framework.response import Response
import random
import string

from apps.account.serializers import SerializerCreateAccount
from apps.users.models import ModelsUser, ModelsSatus
from apps.account.models import ModelsAccount
from apps.users.serializers import SignUpSerializer, serialize_errors, SerializerUser, SerializerSatus
from django.conf import settings
from django.core.mail import send_mail


def send_auth_mail(subject, recipient, password):
    host = settings.EMAIL_HOST_USER
    email = recipient.email
    message = f'username: {recipient.email}\npassword: {password}'
    send_mail(subject, message, host, [email])


def generate_password():
    password_characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(password_characters) for i in range(8))
    return password


def create_profile(user, data):
    step = 0
    try:
        step = int(data['step'])
    except:
        pass
    try:
        email = data['email']
    except:
        return Response({
            'success': False,
            'errors': ["Email wasn't entered"]
        }, status=status.HTTP_400_BAD_REQUEST)
    if step == 1:
        if ModelsUser.objects.filter(email=email, is_active=True):
            return Response({
                'success': False,
                'errors': ['User with this email already exists. Try again with new email address.']
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            data._mutable = True
            password = generate_password()
            data['password'] = password
            serializer = SignUpSerializer(data=data)
            data._mutable = False
            if serializer.is_valid():
                valid_data = serializer.validated_data
                email, password = valid_data['email'], valid_data['password']
                user = ModelsUser.objects.create_user(username=email, email=email, password=password)
            else:
                return Response({
                    'success': False,
                    'errors': serialize_errors(serializer.errors)
                }, status=status.HTTP_400_BAD_REQUEST)
        user.is_active = True
        user.save()
        send_auth_mail('signup', user, password)
        return Response({
            'success': True,
            'data': {
                'email': user.email,
            }
        }, status=status.HTTP_201_CREATED)
    elif step == 2:
        try:
            user = ModelsUser.objects.get(id=user.id)
            account = ModelsAccount.objects.get(id=user.account_id_id)
            print(account)
        except:
            return Response({
                'success': False,
            }, status=status.HTTP_400_BAD_REQUEST)

        if ModelsUser.objects.filter(email=email, is_active=True):
            return Response({
                'success': False,
                'errors': ['User with this email already exists. Try again with new email address.']
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            data._mutable = True
            password = generate_password()
            data['password'] = password
            serializer = SignUpSerializer(data=data)
            data._mutable = False
            if serializer.is_valid():
                valid_data = serializer.validated_data
                email, password = valid_data['email'], valid_data['password']
                user = ModelsUser.objects.create_user(
                    username=email, email=email, password=password
                )
            else:
                return Response({
                    'success': False,
                    'errors': serialize_errors(serializer.errors)
                }, status=status.HTTP_400_BAD_REQUEST)
        user.account_id = account
        user.is_active = True
        user.save()
        send_auth_mail('signup', user, password)
        return Response({
            'success': True,
            'data': {
                'email': user.email,
            }
        }, status=status.HTTP_201_CREATED)


def create_account(user, data):
    try:
        name = data['name']
    except:
        return Response({
            'success': False,
            'errors': ["name wasn't entered"]
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = ModelsUser.objects.get(id=user.id)
    except:
        return Response({
            'success': False,
        }, status=status.HTTP_400_BAD_REQUEST)
    if ModelsAccount.objects.filter(name=name):
        return Response({
            'success': False,
            'errors': ['Account with this name already exists. Try again with new name.']
        }, status=status.HTTP_400_BAD_REQUEST)
    else:
        serializer = SerializerCreateAccount(data=data)
        if serializer.is_valid():
            account = ModelsAccount.objects.create(name=name)
        else:
            return Response({
                'success': False,
                'errors': serialize_errors(serializer.errors)
            }, status=status.HTTP_400_BAD_REQUEST)
    account.save()
    user.account_id = account
    user.save()
    return Response({
        'success': True,
        'data': {
            'account': account.name,
        }
    }, status=status.HTTP_201_CREATED)


def get_user_list(user):
    print(user)
    print(user.account_id)
    user = ModelsUser.objects.get(id=user.id, is_active=True)
    users = ModelsUser.objects.filter(account_id=user.account_id_id)
    return Response({
        'success': True,
        'users': SerializerUser(users, many=True).data,
    }, status=status.HTTP_200_OK)


def get_status_list():
    statuses = ModelsSatus.objects.all()
    return Response({
        'success': True,
        'users': SerializerSatus(statuses, many=True).data,
    }, status=status.HTTP_200_OK)
