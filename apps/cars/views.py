from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .logic import (
    create_car, get_car,
    update_car, delete_car
)


class ViewCar(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return create_car(request)


class ViewGetCar(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return get_car(request)

    def put(self, request):
        return update_car(request)

    def delete(self, request):
        return delete_car(request)
