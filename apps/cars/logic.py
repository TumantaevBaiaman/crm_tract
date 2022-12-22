from rest_framework import status
from rest_framework.response import Response

from . import models, serializers
from ..users.logic.logic import check_auth
from ..users.serializers import serialize_errors


def extract_request_data(request):
    data = {}
    if request.data:
        data = {k: v for k, v in request.data.items()}
    else:
        data['error'] = 'BAD_REQUEST'
    return data


@check_auth('employee')
def create_car(user, data):
    try:
        serializer = serializers.SerializerCar(data=data)
        if serializer.is_valid():
            serializer.save(account=user.account_id)
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
def get_car(user, data):
    if 'id' in list(data.keys()):
        car = models.ModelsCars.objects.get(
            id=data["id"],
            deleted=False
        )
        return Response({
            'success': True,
            'car': serializers.SerializerCar(car).data,
        }, status=status.HTTP_200_OK)
    else:
        car = models.ModelsCars.objects.filter(account=user.account_id, deleted=False)
        return Response({
            'success': True,
            'car': serializers.SerializerCar(car, many=True).data,
        }, status=status.HTTP_200_OK)



@check_auth('employee')
def update_car(user, data):
    try:
        id = data['id']
        car = models.ModelsCars.objects.get(id=id, deleted=False)
    except:
        return Response({
            'success': False,
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        serializer = serializers.SerializerCar(
            car,
            data=data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'car': serializers.SerializerCar(car).data,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({
            'success': False,
        }, status=status.HTTP_400_BAD_REQUEST)


@check_auth('employee')
def delete_car(user, data):
    try:
        id = data['id']
        car = models.ModelsCars.objects.get(id=id, deleted=False)
    except:
        return Response({
            'success': False,
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        car.deleted = True
        car.save()
        return Response({
            'success': True
        },
            status=status.HTTP_200_OK
        )
    except:
        return Response({
            'success': False,
        }, status=status.HTTP_400_BAD_REQUEST)

