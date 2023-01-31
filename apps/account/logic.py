from rest_framework import status
from rest_framework.response import Response

from apps.account.models import ModelsAccount
from apps.account.serializers import SerializerAccount
from apps.users.logic.logic import check_auth
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


@check_auth('admin')
def get_update_account(user, data):
    try:
        id = data['id']
        account = ModelsAccount.objects.get(id=id)
    except:
        return Response({
            'success': False,
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        serializer = SerializerAccount(
            account,
            data=data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'account': SerializerAccount(account).data,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({
            'success': False,
        }, status=status.HTTP_400_BAD_REQUEST)

