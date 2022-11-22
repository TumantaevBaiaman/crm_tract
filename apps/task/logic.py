
from . import models


def extract_request_data_task(request):
    data = {}
    user = request.user.id

    if request.data:
        data = {k: v for k, v in request.data.items()}
    else:
        data['error'] = 'BAD_REQUEST'
    return data


def create_task(data):

    try:
        customer = models.ModelsTask.objects.create(
            invoice_id_id=data['invoice_id'],
            work=data['work'],
            payment=data['payment']
        )
        customer.save()

    except BaseException as ex:
        return {'success': 'False'}