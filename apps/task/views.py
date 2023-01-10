from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from apps.task.logic import create_task, get_tasks


class ViewCreateTask(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return create_task(request)


class ViewGetTask(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return get_tasks(request)