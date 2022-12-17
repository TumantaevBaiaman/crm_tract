from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .logic.logic import create_profile, create_account, get_user_list
from .models import ModelsUser


class ViewRegisterAccount(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return create_account(request.user, request.data)


class ViewRegisterUser(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        return create_profile(request.user, request.data)


class LoginView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request, *args, **kwargs):
        if 'email' in request.data.keys():
            users = ModelsUser.objects.filter(email=request.data['email'], is_active=True)
            if len(users) == 1:
                data = super(LoginView, self).post(request, *args, **kwargs)
                return data
        return Response({
            'detail': "No active account found with the given credentials",
        }, status=status.HTTP_401_UNAUTHORIZED)


class ViewListUser(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return get_user_list(request.user)
