from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.invoice.logic import extract_request_data
from apps.task.logic import create_task, get_tasks, update_tasks, export_task


class ViewCreateTask(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return update_tasks(request)


class ViewGetTask(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return get_tasks(request)

class ViewUpdateTask(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return update_tasks(request)


class TaskExportView(APIView):
    def post(self, request):
        try:
            data = extract_request_data(request)
            action_name = data['action']
            actions = {
                'export': export_task,
            }
            action = actions[action_name]
            return action(request)
        except BaseException as ex:
            print(ex)
            return Response({
                'success': False,
            }, status=status.HTTP_400_BAD_REQUEST)
