from rest_framework.views import APIView

from apps.invoice.logic import get_invoice


class ViewGetInvoice(APIView):

    def post(self, request):
        return get_invoice(request)

    def get(self, request):
        return get_invoice(request)

