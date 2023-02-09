from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .logic.logic import create_profile, create_account, get_user_list, get_status_list, get_profile, update_profile, \
    new_reg_user
from .models import ModelsUser


class ViewRegisterAccount(APIView):

    def post(self, request):
        return create_account(request)


class ViewListStatus(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        return get_status_list(request)


class ViewRegisterUser(APIView):
    permission_classes = (AllowAny,)
    # authentication_classes = ()

    def post(self, request):
        return create_profile(request)


class ViewRegisterNewUser(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request):
        return new_reg_user(request)


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
        return get_user_list(request)


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return get_profile(request)

    def put(self, request):
        return update_profile(request)
