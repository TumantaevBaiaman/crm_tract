from . import models


def extract_request_data(request):
    data = {}
    user = request.user.id

    if request.data:
        data = {k: v for k, v in request.data.items()}
        data['user'] = user
    else:
        data['error'] = 'BAD_REQUEST'
    return data


def create_customer(data):

    try:
        customer = models.ModelsCustomer.objects.create(
            user_id=data['user'],
            full_name=data['full_name'],
            last_name=data['last_name'],
            address=data['address']
        )
        customer.save()

    except BaseException as ex:
        return {'success': 'False'}


