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


def extract_request_data(request):
    data = {}
    if request.data:
        data = {k: v for k, v in request.data.items()}
    elif request.query_params:
        data = {k: v for k, v in request.query_params.items()}
    data['meta'] = request.META.copy()
    return data


def check_auth(access_status=None):
    def real_decorator(original_function):
        def wrapper(request, is_jwt=True):
            data = extract_request_data(request)
            user = False
            status_model = False
            if is_jwt:
                if request.auth:
                    if request.user:
                        if request.user.is_active:
                            if ModelsUser.objects.filter(id=request.user.id):
                                user = ModelsUser.objects.get(id=request.user.id)
                                if user.status_id:
                                    status_model = ModelsSatus.objects.get(id=user.status_id).name
            else:
                pass
            status_list = ('employee', 'admin')
            print(user)
            if status_model == status_list[-1]:
                return original_function(user, data)
            elif access_status in status_list and user:
                if status_model == access_status:
                    return original_function(user, data)
                return Response({
                    'success': False,
                }, status=status.HTTP_403_FORBIDDEN)

            elif access_status is None:
                return original_function(user, data)
            return Response({
                'success': False,
            }, status=status.HTTP_403_FORBIDDEN)
        return wrapper
    return real_decorator


def send_auth_mail(subject, recipient, password):
    host = settings.EMAIL_HOST_USER
    email = recipient.email
    message = f'username: {recipient.email}\npassword: {password}'
    send_mail(subject, message, host, [email])


def generate_password():
    password_characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(password_characters) for i in range(8))
    return password


@check_auth()
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
            password = generate_password()
            data['password'] = password
            serializer = SignUpSerializer(data=data)
            if serializer.is_valid():
                valid_data = serializer.validated_data
                email, password = valid_data['email'], valid_data['password']
                user = ModelsUser.objects.create_user(
                    username=email,
                    email=email,
                    password=password
                )
            else:
                return Response({
                    'success': False,
                    'errors': serialize_errors(serializer.errors)
                }, status=status.HTTP_400_BAD_REQUEST)
        user.is_active = True
        user.lastname = data['lastname'] if data['lastname'] else None
        user.phone = data['phone'] if data['phone'] else None
        user.date_of_birth = data['date_of_birth'] if data['date_of_birth'] else None
        user.is_active = True
        user.save()
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
            user_status = str(data['status'])
        except:
            pass
        try:
            user = ModelsUser.objects.get(id=user.id)
            account = ModelsAccount.objects.get(id=user.account_id_id)
            status_name = ModelsSatus.objects.get(id=user.status_id).name
            status_name = ModelsSatus.objects.get(id=user.status_id).name
        except:
            return Response({
                'success': False,
            }, status=status.HTTP_400_BAD_REQUEST)
        if status_name != 'admin' and account:
            return Response({
                'success': False,
            }, status=status.HTTP_403_FORBIDDEN)
        if ModelsUser.objects.filter(email=email, is_active=True):
            return Response({
                'success': False,
                'errors': ['User with this email already exists. Try again with new email address.']
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            password = generate_password()
            data['password'] = password
            serializer = SignUpSerializer(data=data)
            if serializer.is_valid():
                valid_data = serializer.validated_data
                email, password = valid_data['email'], valid_data['password']
                user = ModelsUser.objects.create_user(
                    username=email,
                    email=email,
                    password=password
                )
            else:
                return Response({
                    'success': False,
                    'errors': serialize_errors(serializer.errors)
                }, status=status.HTTP_400_BAD_REQUEST)
        user.account_id = account
        user.lastname = data['lastname'] if data['lastname'] else None
        user.status = ModelsSatus.objects.get(name=user_status)
        user.phone = data['phone'] if data['phone'] else None
        user.date_of_birth = data['date_of_birth'] if data['date_of_birth'] else None
        user.is_active = True
        user.save()
        send_auth_mail('signup', user, password)
        return Response({
            'success': True,
            'data': {
                'email': user.email,
            }
        }, status=status.HTTP_201_CREATED)


@check_auth()
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
    status_name = ModelsSatus.objects.get(name='admin')
    user.account_id = account
    user.status_id = status_name
    user.save()
    return Response({
        'success': True,
        'data': {
            'account': account.name,
        }
    }, status=status.HTTP_201_CREATED)


@check_auth('admin')
def get_user_list(user, data):
    user = ModelsUser.objects.get(id=user.id, is_active=True)
    users = ModelsUser.objects.filter(account_id=user.account_id_id)
    return Response({
        'success': True,
        'users': SerializerUser(users, many=True).data,
    }, status=status.HTTP_200_OK)


@check_auth()
def get_status_list(user, data):
    statuses = ModelsSatus.objects.all()
    return Response({
        'success': True,
        'users': SerializerSatus(statuses, many=True).data,
    }, status=status.HTTP_200_OK)
