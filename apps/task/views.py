from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from apps.task.logic import create_task, get_tasks, update_tasks


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
"""
{
"car_id": 1, 
"invoice_id": 1,
"update_tasks": 
    [
        {
          "id": 17, 
          "work": "kjsh", 
          "payment": 570,
          "car_id": 1
        }
    ], 
"new_tasks": [
        { 
          "work": "hsfjah", 
          "payment": 7000
          
        }, 
        {
          "work": "jhhjhjjhgfdssdfgh", 
          "payment": 8800}
    ], 
"del_tasks": [18]
}
"""
