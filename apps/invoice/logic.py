
from . import models


def extract_request_data(request):
    data = {}
    user = request.user.id

    if request.data:
        data = {k: v for k, v in request.data.items()}
        data['crew_id'] = user
    else:
        data['error'] = 'BAD_REQUEST'
    return data


def create_invoice(data):

    try:
        customer = models.ModelsInvoice.objects.create(
            crew_id_id=data['crew_id'],
            car_id_id=data['car_id'],
            description=data['description']
        )
        customer.save()

    except BaseException as ex:
        return {'success': 'False'}