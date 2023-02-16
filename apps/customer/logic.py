from rest_framework import status
from rest_framework.response import Response
import re
from . import models, serializers
from ..cars.models import ModelsCars
from ..cars.serializers import SerializerCar
from ..invoice.models import ModelsInvoice
from ..invoice.serializers import SerializerInvoice
from ..users.logic.logic import check_auth
from ..users.serializers import serialize_errors


def extract_request_data(request):
    data = {}
    user = request.user.id

    if request.data:
        data = {k: v for k, v in request.data.items()}
        data['user'] = user
    else:
        data['error'] = 'BAD_REQUEST'
    return data


@check_auth('employee')
def create_customer(user, data):
    try:
        emails = data['email']
        text = re.sub(r'\s+', '', emails.strip())
        # list_emails = text.split(",")
        list_emails = text
        serializer = serializers.SerializerCustomer(data=data)
        if serializer.is_valid():
            customer = models.ModelsCustomer.objects.create(
                user_id=user.id,
                account=user.account_id,
                email=list_emails,
                full_name=data['full_name'],
                street1=data['street1'],
                street2=data['street2'],
                country=data['country'],
                phone=data['phone'],
                phone2=data['phone2'],
                postal_code=data['postal_code']
            )
            customer.save()
            return Response({
                'success': True
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'errors': serialize_errors(serializer.errors)
            }, status=status.HTTP_400_BAD_REQUEST)
    except BaseException as ex:
        return Response({
            'success': False,
        }, status=status.HTTP_400_BAD_REQUEST)


@check_auth('employee')
def get_customers(user, data):
    if 'id' in list(data.keys()):
        customer = models.ModelsCustomer.objects.get(
            id=data["id"], deleted=False
        )
        print(customer)
        cars = ModelsCars.objects.filter(customer=customer, deleted=False)
        invoices = ModelsInvoice.objects.filter(customer_id=customer)
        print(invoices)
        return Response({
            'success': True,
            'customer': serializers.SerializerCustomer(customer).data,
            'cars': SerializerCar(cars, many=True).data,
            'invoices': SerializerInvoice(invoices, many=True).data,
        }, status=status.HTTP_200_OK)

    else:
        customers = models.ModelsCustomer.objects.filter(account=user.account_id, deleted=False)
        print(customers)
        return Response({
            'success': True,
            'customers': serializers.SerializerCustomer(customers, many=True).data,
        }, status=status.HTTP_200_OK)


@check_auth('employee')
def update_customers(user, data):
    try:
        id = data['id']
        customer = models.ModelsCustomer.objects.get(id=id, deleted=False)
    except:
        return Response({
            'success': False,
            'errors': ["id wasn't entered"]
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        serializer = serializers.SerializerCustomer(
            customer,
            data=data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'customers': serializers.SerializerCustomer(customer).data,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({
            'success': False,
        }, status=status.HTTP_400_BAD_REQUEST)


@check_auth('admin')
def get_all_customers(user, data):
    customers = models.ModelsCustomer.objects.filter(account=user.account_id, deleted=False)
    return Response({
        'success': True,
        'customers': serializers.SerializerCustomer(customers, many=True).data,
    }, status=status.HTTP_200_OK)


@check_auth('employee')
def delete_customers(user, data):
    try:
        id = data['id']
        customer = models.ModelsCustomer.objects.get(id=id)
    except:
        return Response({
            'success': False,
            'errors': ["id wasn't entered"]
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        customer.deleted = True
        customer.save()
        return Response({
            'success': True
        },
            status=status.HTTP_200_OK
        )
    except:
        return Response({
            'success': False,
        }, status=status.HTTP_400_BAD_REQUEST)



