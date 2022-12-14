from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.views import APIView
from .logic.logic import create_profile, create_account


class ViewRegisterAccount(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return create_account(request.user, request.data)


class ViewRegisterUser(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        return create_profile(request.user, request.data)
