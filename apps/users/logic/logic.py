from apps.users.models import ModelsUser
from apps.account.models import ModelsAccount


class CreateAccount:

    def __init__(self, data_user, data_account):
        self.request_data_account = data_account
        self.request_data_user = data_user

    def create(self):

        account = ModelsAccount.objects.create(
            name=self.request_data_account['name'],
            status_id=self.request_data_account['status']
        )

        user = ModelsUser.objects.create(
            account_id=account,
            email=self.request_data_user['email'],
            status_id=self.request_data_user['status'],
            password=self.request_data_user['password'],
            username=self.request_data_user['username'],
            lastname=self.request_data_user['lastname'],
            date_of_birth=self.request_data_user['date_of_birth'],
            phone=self.request_data_user['phone']
        )
        return user


class CreateUser:

     def __init__(self, data):
         self.data = data

     def create(self):
         account = ModelsAccount.objects.get(id=self.data['account_id'])
         print(account)
         user = ModelsUser.objects.create(
             account_id=account,
             email=self.data['email'],
             status_id=self.data['status'],
             password=self.data['password'],
             username=self.data['username'],
             lastname=self.data['lastname'],
             date_of_birth=self.data['date_of_birth'],
             phone=self.data['phone']
         )
         return user

