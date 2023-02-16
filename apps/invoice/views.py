from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.invoice.logic import (
    get_invoice, extract_request_data,
    generate_pdf_list_invoice,
    generate_pdf_for_detailed_invoice,
    export_invoices_csv, update_status_inv,
    get_filter_invoice, get_customer_report,
    get_crew_report, get_my_day, get_tax, get_statistics
)


class ViewGetInvoice(APIView):

    def post(self, request):
        return get_invoice(request)

    def get(self, request):
        return get_invoice(request)


class InvoiceListExport(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        print('hello')
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


class ViewStatusInvoice(APIView):

    def post(self, request):
        return update_status_inv(request)


class InvoiceFilterView(APIView):

    def post(self, request):
        return get_filter_invoice(request)


class InvoiceCustomerReportView(APIView):

    def post(self, request):
        return get_customer_report(request)


class InvoiceCrewReportView(APIView):

    def post(self, request):
        return get_crew_report(request)

class InvoiceMyDay(APIView):

    def post(self, request):
        print(request.data)
        return get_my_day(request)


class InvoiceTax(APIView):

    def post(self, request):
        return get_tax(request)


class InvoiceStatistics(APIView):

    def post(self, request):
        return get_statistics(request)
