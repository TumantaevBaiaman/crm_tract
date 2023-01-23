from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.invoice.logic import get_invoice, extract_request_data, generate_pdf_list_invoice, \
    generate_pdf_for_detailed_invoice, export_invoices_csv


class ViewGetInvoice(APIView):

    def post(self, request):
        return get_invoice(request)

    def get(self, request):
        return get_invoice(request)


class InvoiceListExport(APIView):

    def post(self, request):
        try:
            data = extract_request_data(request)
            action_name = data['action']
            actions = {
                'export': generate_pdf_list_invoice,
            }
            action = actions[action_name]
            return action(request)
        except BaseException as ex:
            print(ex)
            return Response({
                'success': False,
            }, status=status.HTTP_400_BAD_REQUEST)


class InvoiceExport(APIView):

    def post(self, request):
        try:
            data = extract_request_data(request)
            action_name = data['action']
            actions = {
                'export': generate_pdf_for_detailed_invoice,
            }
            action = actions[action_name]
            return action(request)
        except BaseException as ex:
            print(ex)
            return Response({
                'success': False,
            }, status=status.HTTP_400_BAD_REQUEST)


class InvoiceExportCSV(APIView):

    def post(self, request):
        try:
            data = extract_request_data(request)
            action_name = data['action']
            actions = {
                'export': export_invoices_csv,
            }
            action = actions[action_name]
            return action(request)
        except BaseException as ex:
            print(ex)
            return Response({
                'success': False,
            }, status=status.HTTP_400_BAD_REQUEST)

