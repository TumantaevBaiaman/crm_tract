from . import models


def extract_request_data(request):
    data = {}
    if request.data:
        data = {k: v for k, v in request.data.items()}
    else:
        data['error'] = 'BAD_REQUEST'
    return data


def create_car(data):

    try:
        car = models.ModelsCars.objects.create(
            customer_id=data['customer'],
            description=data['description'],
            vin=data['vin'],
            model=data['model'],
            image=data['image']
        )
        car.save()

    except BaseException as ex:
        return {'success': 'False'}