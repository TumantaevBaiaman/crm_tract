from django.db.models import Sum
from rest_framework import status
from rest_framework.response import Response

from .models import ModelsTask
from .serializers import SerializerTask
from ..cars.models import ModelsCars
from ..customer.models import ModelsCustomer
from ..invoice.models import ModelsInvoice
from ..invoice.serializers import SerializerInvoice
from ..users.logic.logic import check_auth


def extract_request_data_task(request):
    data = {}
    user = request.user.id

    if request.data:
        data = {k: v for k, v in request.data.items()}
    else:
        data['error'] = 'BAD_REQUEST'
    return data


@check_auth('employee')
def create_task(user, data):
    try:
        car = ModelsCars.objects.get(id=data['car_id'])
    except:
        return Response({
            'success': False,
            'errors': ["car id wasn't entered"]
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        task_list = []
        tasks = data['tasks']
        for task_item in tasks:
            task = ModelsTask(**task_item)
            task.car_id = ModelsCars.objects.get(id=car.id)
            task_list.append(task)
        tasks = ModelsTask.objects.bulk_create(task_list)

        invoice = ModelsInvoice.objects.create(
            crew_id=user,
            car_id=car,
            customer_id=car.customer,
        )
        invoice.tasks.add(*tasks)
        total_price = ModelsTask.objects.filter(pk__in=[task.pk for task in tasks]).aggregate(Sum('payment'))[
            'payment__sum']
        invoice.total_sum = total_price
        invoice.save()

        return Response({
            'success': True,
            'tasks': SerializerTask(tasks, many=True).data,
            'invoice': SerializerInvoice(invoice).data
        }, status=status.HTTP_201_CREATED)

    except BaseException as ex:
        return Response({
            'success': False,
        }, status=status.HTTP_400_BAD_REQUEST)


@check_auth('employee')
def get_tasks(user, data):
    if 'id_invoice' in list(data.keys()):
        invoice = ModelsInvoice.objects.get(
            id=data["id_invoice"]
        )
        tasks = invoice.tasks.all()
        return Response({
            'success': True,
            'tasks': SerializerTask(tasks, many=True).data,
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'success': False,
        }, status=status.HTTP_400_BAD_REQUEST)


@check_auth('employee')
def update_tasks(user, data):
    tasks_new = []
    try:
        car = ModelsCars.objects.get(id=data['car_id'], deleted=False)
    except:
        return Response({
            'success': False,
            'errors': ["car id wasn't entered"]
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        if data['update_tasks']:
            tasks_update = data['update_tasks']
            for task_item in tasks_update:
                obj = ModelsTask.objects.get(id=task_item['id'])
                obj.work = task_item['work']
                obj.payment = task_item['payment']
                obj.save()

        if data['del_tasks']:
            tasks_del = data['del_tasks']
            for task_item in tasks_del:
                obj = ModelsTask.objects.get(id=task_item)
                obj.delete()

        if data['new_tasks']:
            task_list = []
            tasks = data['new_tasks']
            for task_item in tasks:
                task = ModelsTask(**task_item)
                task.car_id = ModelsCars.objects.get(id=car.id)
                task_list.append(task)
            tasks_new = ModelsTask.objects.bulk_create(task_list)
        if 'invoice_id' in list(data.keys()):
            invoice = ModelsInvoice.objects.get(id=data['invoice_id'])
        else:
            print(data)
            invoice = ModelsInvoice.objects.create(
                crew_id=user,
                car_id=car,
                customer_id=car.customer,
                account_id=data["account"],
            )
        if tasks_new:
            invoice.tasks.add(*tasks_new)
        tasks = invoice.tasks.all()

        total_price = ModelsTask.objects.filter(pk__in=[task.pk for task in tasks]).aggregate(Sum('payment'))[
            'payment__sum']
        invoice.total_sum = total_price
        invoice.save()

        return Response({
            'success': True,
            'tasks': SerializerTask(tasks, many=True).data,
            'invoice': SerializerInvoice(invoice).data
        }, status=status.HTTP_201_CREATED)

    except BaseException as ex:
        return Response({
            'success': False,
        }, status=status.HTTP_400_BAD_REQUEST)


@check_auth()
def export_task(profile, data):
    pass



