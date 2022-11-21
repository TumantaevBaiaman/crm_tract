from apps.users.models import ModelsSatus


def request_data_account(data):
    data_account = {
        'name': data['account_name'],
        'status': ModelsSatus.objects.get(name='admin').id
    }
    return data_account


def request_data_user(data):
    data_user = {
        'email': data['email'],
        'status': ModelsSatus.objects.get(name='admin').id,
        'password': data['password'],
        'username': data['username'],
        'lastname': data['lastname'],
        'date_of_birth': data['date_of_birth'],
        'phone': data['phone']
    }
    return data_user