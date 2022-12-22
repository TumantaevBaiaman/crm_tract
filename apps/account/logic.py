from rest_framework import status
from rest_framework.response import Response

from apps.account.models import ModelsAccount
from apps.account.serializers import SerializerAccount
from apps.users.models import ModelsUser
from apps.users.serializers import SerializerUser


def get_account(user, data):
    try:
        account = ModelsAccount.objects.get(id=user.account_id_id)
        user = ModelsUser.objects.get(id=user.id)
        return Response({
            'success': True,
            'account': SerializerAccount(account).data,
            'user': SerializerUser(user).data,
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'success': False,
        }, status=status.HTTP_400_BAD_REQUEST)

