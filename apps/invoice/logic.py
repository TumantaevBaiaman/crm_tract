from rest_framework import status
from rest_framework.response import Response

from . import models
from .serializers import SerializerInvoice
from ..cars.serializers import SerializerCar
from ..users.logic.logic import check_auth


def extract_request_data(request):
    data = {}
    user = request.user.id

    if request.data:
        data = {k: v for k, v in request.data.items()}
        data['crew_id'] = user
    else:
        data['error'] = 'BAD_REQUEST'
    return data


@check_auth('employee')
def get_invoice(user, data):
    if 'id' in list(data.keys()):
        invoice = models.ModelsInvoice.objects.get(
            id=data["id"],
        )
        return Response({
            'success': True,
            'invoice': SerializerInvoice(invoice).data,
        }, status=status.HTTP_200_OK)
    else:
        invoice = models.ModelsInvoice.objects.filter(crew_id=user)
        return Response({
            'success': True,
            'invoice': SerializerInvoice(invoice, many=True).data,
        }, status=status.HTTP_200_OK)
