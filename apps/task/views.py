from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from . import logic
from . import serializers


class ViewCreateTask(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:
            data = logic.extract_request_data_task(request)
            serializer = serializers.SerializerCreateTask(data=data)
            if serializer.is_valid():
                logic.create_task(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except BaseException as ex:
            return Response({
                'success': False,
            }, status=status.HTTP_400_BAD_REQUEST)

