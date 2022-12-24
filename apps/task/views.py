from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from apps.task.logic import create_task


class ViewCreateTask(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return create_task(request)

class Test(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return create_invoice(request)