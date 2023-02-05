import csv
import json
import pandas as pd
from django.conf import settings
from django.db.models import Sum
from pytz import timezone
from rest_framework import status
from rest_framework.response import Response
import os
from datetime import datetime
from django.core.files.storage import default_storage
from django.http import HttpResponse
from borb.pdf import Document
from borb.pdf import Page
from borb.pdf import SingleColumnLayout
from borb.pdf import PageLayout
from decimal import Decimal
from borb.pdf import Image
from borb.pdf import FixedColumnWidthTable
from borb.pdf import Paragraph
from borb.pdf import Alignment
from borb.pdf import TableCell
from borb.pdf import PDF
from borb.pdf.canvas.layout.layout_element import LayoutElement
import io
from pathlib import Path
from PIL import Image as IM

from . import models as models
from .serializers import SerializerInvoice
from ..account.models import ModelsAccount
from ..account.serializers import SerializerAccount
from ..customer.models import ModelsCustomer
from ..users.logic.logic import check_auth, send_email_with_pdf_attachment
from ..users.models import ModelsUser


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return json.JSONEncoder.default(self, obj)


def query_invoice(user, data):
    try:
        tz = timezone('UTC')
        start_date = datetime.strptime(data['start_date'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)
        end_date = datetime.strptime(data['end_date'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)
        invoices = models.ModelsInvoice.objects.filter(
            crew_id__account_id=user.account_id,
            finished_at__range=(start_date, end_date)
        )
        return invoices
    except:
        return Response({
            'success': False,
        }, status=status.HTTP_400_BAD_REQUEST)



def extract_request_data(request):
    data = {}
    user = request.user.id

    if request.data:
        data = {k: v for k, v in request.data.items()}
        data['crew_id'] = user
    else:
        data['error'] = 'BAD_REQUEST'
    return data


@check_auth('employee')
def get_invoice(user, data):
    if 'id' in list(data.keys()):
        invoice = models.ModelsInvoice.objects.get(
            id=data["id"],
        )
        account = invoice.crew_id.account_id
        return Response({
            'success': True,
            'account': SerializerAccount(account).data,
            'invoice': SerializerInvoice(invoice).data,
        }, status=status.HTTP_200_OK)
    else:
        invoices = models.ModelsInvoice.objects.filter(crew_id=user)
        account = user.account_id
        return Response({
            'success': True,
            'account': SerializerAccount(account).data,
            'invoice': SerializerInvoice(invoices, many=True).data,
        }, status=status.HTTP_200_OK)


def get_filter_invoice(request):
    data = extract_request_data(request)
    tz = timezone('UTC')
    try:

        from_date = data['from_date']
        to_date = data['to_date']
    except:
        return Response({
            'success': False,
        }, status=status.HTTP_400_BAD_REQUEST)

    crew = data['crew'] if data['crew'] else None
    car_id = data['car_id'] if data['car_id'] else None
    customer_id = data['customer_id'] if data['customer_id'] else None
    number = data['number'] if data['number'] else None
    finished_at = data['finished_at'] if data['finished_at'] else None
    start_at = data['start_at'] if data['start_at'] else None
    page = data['page'] if data['start_at'] else 1
    page_size = data['page_size'] if data['start_at'] else 10

    invoices = models.ModelsInvoice.objects.all()
    invoices = invoices.filter(
        finished_at__range=(
            datetime.strptime(from_date + ' 00:00:00', "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz),
            datetime.strptime(to_date + ' 23:59:59', "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)

        )
    )
    if number is not None:
        invoices = invoices.filter(number=number)
    if crew is not None:
        invoices = invoices.filter(crew_id=crew)
    if car_id is not None:
        invoices = invoices.filter(car_id=car_id)
    if customer_id is not None:
        invoices = invoices.filter(customer_id=customer_id)
    if finished_at is not None and start_at is None:
        invoices = invoices.filter(
            finished_at__range=(
                datetime.strptime(data['finished_at']+' 00:00:00', "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz),
                datetime.strptime(data['finished_at']+' 23:59:59', "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)

            )
        )
    if start_at is not None and finished_at is None:
        invoices = invoices.filter(
            start_at__range=(
                datetime.strptime(data['start_at'] + ' 00:00:00', "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz),
                datetime.strptime(data['start_at'] + ' 23:59:59', "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)
            )
        )
    distinct_customer_ids = invoices.values_list('customer_id', flat=True).distinct()
    response = []
    for customer in distinct_customer_ids:
        customer_data = ModelsCustomer.objects.get(id=customer)
        customer_invoices = invoices.filter(customer_id=customer_data)
        total_sum_invoice = customer_invoices.aggregate(Sum('total_sum'))['total_sum__sum']
        response_data = {
            'customer_name': customer_data.full_name,
            'invoices': SerializerInvoice(customer_invoices, many=True).data,
            'total_sum_invoice': total_sum_invoice,
            'gross': (total_sum_invoice*13)/100 + total_sum_invoice,
        }
        response.append(response_data)
    total_sum_all_invoices = invoices.aggregate(Sum('total_sum'))['total_sum__sum']
    response.append(
        {
            'total_sum_all_invoices': total_sum_all_invoices,
            'gross_of_all_invoices': (total_sum_all_invoices*13)/100+total_sum_all_invoices,
        })
    return Response(response, status=status.HTTP_200_OK)


@check_auth()
def get_customer_report(user, data):
    account = user.account_id
    list_customers = []
    tz = timezone('UTC')
    try:

        from_date = data['from_date']
        to_date = data['to_date']
    except:
        return Response({
            'success': False,
        }, status=status.HTTP_400_BAD_REQUEST)
    invoices = models.ModelsInvoice.objects.filter(
        start_at__range=(
            datetime.strptime(from_date + ' 00:00:00', "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz),
            datetime.strptime(to_date + ' 23:59:59', "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)

        ),
        status='final'
    )
    all_customers = [invoice.customer_id for invoice in invoices]
    all_customers = set(all_customers)
    customers = [customer for customer in all_customers if customer.account == account]

    gross = 0
    total_invoice_sum = 0
    if len(customers) >=1:
        for customer in customers:
            invoice_customer = invoices.filter(customer_id=customer)
            customer_inv_sum = invoice_customer.aggregate(Sum('total_sum'))['total_sum__sum']
            customer_gross = (customer_inv_sum*13)/100 + customer_inv_sum
            customer_data = {}
            customer_data['id'] = customer.id
            customer_data['full_name'] = customer.full_name
            customer_data['invoice_count'] = invoice_customer.count()
            customer_data['total_sum'] = customer_inv_sum
            customer_data['gross'] = customer_gross

            list_customers.append(customer_data)

            total_invoice_sum += customer_inv_sum
            gross += customer_gross


    return Response({
        'list_customers': list_customers,
        'total_count': invoices.count(),
        'total_all_sum': total_invoice_sum,
        'total_gross': gross
    }, status=status.HTTP_200_OK)


@check_auth()
def get_crew_report(user, data):
    account = user.account_id
    list_crews = []
    tz = timezone('UTC')
    try:

        from_date = data['from_date']
        to_date = data['to_date']
    except:
        return Response({
            'success': False,
        }, status=status.HTTP_400_BAD_REQUEST)
    invoices = models.ModelsInvoice.objects.filter(
        start_at__range=(
            datetime.strptime(from_date + ' 00:00:00', "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz),
            datetime.strptime(to_date + ' 23:59:59', "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)

        ),
        status='final',

    )
    all_crews = [invoice.crew_id for invoice in invoices]
    all_crews = set(all_crews)
    crews = [crew for crew in all_crews if crew.account_id == account]
    gross = 0
    total_invoice_sum = 0
    if len(crews) >=1:
        for crew in crews:
            invoice_crew = invoices.filter(crew_id=crew)
            crew_inv_sum = invoice_crew.aggregate(Sum('total_sum'))['total_sum__sum']
            crew_gross = (crew_inv_sum*13)/100 + crew_inv_sum
            crew_data = {}
            crew_data['id'] = crew.id
            crew_data['username'] = crew.username
            crew_data['invoice_count'] = invoice_crew.count()
            crew_data['total_sum'] = crew_inv_sum
            crew_data['gross'] = crew_gross

            list_crews.append(crew_data)

            total_invoice_sum += crew_inv_sum
            gross += crew_gross


    return Response({
        'list_customers': list_crews,
        'total_count': invoices.count(),
        'total_all_sum': total_invoice_sum,
        'total_gross': gross
    }, status=status.HTTP_200_OK)


@check_auth()
def get_my_day(user, data):
    try:
        tz = timezone('UTC')
        from_date = data['from_date']
        to_date = data['to_date']
        user_status = str(user.status)
        invoices = models.ModelsInvoice.objects.filter(
            finished_at__range=(
                datetime.strptime(from_date + ' 00:00:00', "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz),
                datetime.strptime(to_date + ' 23:59:59', "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)
            )
        )
    except:
        return Response({
            'success': False,
        }, status=status.HTTP_404_NOT_FOUND)
    try:
        if user_status == 'admin':
            if data['crew_id']:
                invoices = invoices.filter(crew_id_id=data['crew_id'])
            else:
                invoices = invoices.filter(crew_id=user)
        else:
            invoices = invoices.filter(crew_id=user)

        if data['customer_id']:
            invoices = invoices.filter(customer_id_id=data['customer_id'])

        total_sum_all_invoices = invoices.aggregate(Sum('total_sum'))['total_sum__sum']
        gross = (total_sum_all_invoices*13)/100 + total_sum_all_invoices
        return Response({
            'success': True,
            'total_invoice_sum': total_sum_all_invoices,
            'gross': gross,
            'invoices': SerializerInvoice(invoices, many=True).data,
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'success': False,
        }, status=status.HTTP_400_BAD_REQUEST)


@check_auth('admin')
def get_tax(user, data):
    try:
        tz = timezone('UTC')
        from_date = data['from_date']
        to_date = data['to_date']
        invoices = models.ModelsInvoice.objects.filter(
            crew_id__account_id=user.account_id,
            finished_at__range=(
                datetime.strptime(from_date + ' 00:00:00', "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz),
                datetime.strptime(to_date + ' 23:59:59', "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)
            )
        )
    except:
        return Response({
            'success': False,
        }, status=status.HTTP_404_NOT_FOUND)
    try:
        total_sum_all_invoices = invoices.aggregate(Sum('total_sum'))['total_sum__sum']
        gross = (total_sum_all_invoices*13)/100 + total_sum_all_invoices
        tax = (total_sum_all_invoices*13)/100
        invoices_count = invoices.count()
        return Response({
            'success': True,
            'name': 'HST',
            'rate': 13,
            'subtotal': total_sum_all_invoices,
            'gross': gross,
            'invoices_count': invoices_count,
            'tax': tax
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'success': False,
        }, status=status.HTTP_400_BAD_REQUEST)


@check_auth('admin')
def get_statistics(user, data):
    try:
        tz = timezone('UTC')
        from_date = data['from_date']
        to_date = data['to_date']
        account = user.account_id
        invoices = models.ModelsInvoice.objects.filter(
            start_at__range=(
                datetime.strptime(from_date + ' 00:00:00', "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz),
                datetime.strptime(to_date + ' 23:59:59', "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)
            ),
            status='final',
            crew_id__account_id=account
        )
    except:
        return Response({
            'success': False,
        }, status=status.HTTP_404_NOT_FOUND)

    try:
        date_range = pd.date_range(start=from_date, end=to_date)
        date_range_list = date_range.tolist()
        date_range_list = [dt.strftime("%Y-%m-%d") for dt in date_range_list]
        statistics = invoices.extra({'date': "date(start_at)"}).values('date').annotate(
            sum=Sum('total_sum')
        )
        statistics = {stat['date']: stat['sum'] for stat in statistics}
        final_statistics = []
        invoice_count = invoices.count()
        net_revenue = invoices.aggregate(sum=Sum('total_sum'))['sum']
        gross_revenue = net_revenue * Decimal('1.13')
        for date in date_range_list:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            if date in statistics:
                gross = Decimal(statistics[date] * Decimal(13) / 100 + statistics[date])
                final_statistics.append({'date': date, 'sum': statistics[date], 'gross': gross})
            else:
                final_statistics.append({'date': date, 'sum': 0, 'gross': 0})

        return Response({
            'invoice_count': invoice_count,
            'net_revenue': net_revenue,
            'gross_revenue': gross_revenue,
            'statistics': final_statistics

        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'success': False,
        }, status=status.HTTP_400_BAD_REQUEST)


@check_auth('employee')
def update_status_inv(user, data):
    try:
        id = data['id']
        invoice = models.ModelsInvoice.objects.get(id=id)
    except:
        return Response({
            'success': False,
        }, status=status.HTTP_404_NOT_FOUND)
    try:
        invoice.status = data['status']
        invoice.finished_at = datetime.now()
        invoice.save()
        return Response({
            'success': True,
            'invoices': SerializerInvoice(invoice).data,
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'success': False,
        }, status=status.HTTP_400_BAD_REQUEST)


def _build_invoice_information_head_detail(user, data):
    invoice = models.ModelsInvoice.objects.get(
        id=data['invoice_id']
    )
    crew = invoice.crew_id
    account = ModelsAccount.objects.get(id=crew.account_id.id)
    url = account.logo.url.replace('/media/', '')
    #
    image_path = os.path.join(settings.MEDIA_ROOT, url)
    with default_storage.open(image_path, 'rb') as f:
        img = IM.open(f)
        width, height = img.size
    max_size = (128, 128)
    if width > height:
        height = int((max_size[0] / width) * height)
        width = max_size[0]
    else:
        width = int((max_size[1] / height) * width)
        height = max_size[1]

    image: LayoutElement = Image(
        Path(image_path),
        width=Decimal(width),
        height=Decimal(height),
        vertical_alignment=Alignment.MIDDLE
    )
    table_001 = FixedColumnWidthTable(number_of_columns=3, number_of_rows=4)
    table_001.add(Paragraph(" "))
    table_001.add(
        Paragraph("Invoice", font="Helvetica-Bold", font_size=11, horizontal_alignment=Alignment.CENTERED)
    )
    table_001.add(TableCell(image, row_span=4))

    table_001.add(
        Paragraph(f"{account.name}", font="Helvetica-Bold", font_size=12)
    )
    table_001.add(Paragraph(" "))
    table_001.add(
        Paragraph(
            f"""
            {account.street1}
            {account.street2}
            {account.country}
            {account.phone}
            {account.email}
            HST# {account.hst}
            """, font="Helvetica", respect_newlines_in_text=True, font_size=8)
    )
    table_001.add(Paragraph(" "))
    table_001.add(Paragraph(" "))
    table_001.add(Paragraph(" "))

    table_001.no_borders()
    return table_001


def _build_invoice_information_head(user, data):
    invoice = data.first()

    crew = invoice.crew_id
    account = ModelsAccount.objects.get(id=crew.account_id.id)
    url = account.logo.url.replace('/media/', '')

    image_path = os.path.join(settings.MEDIA_ROOT, url)

    with default_storage.open(image_path, 'rb') as f:
        img = IM.open(f)
        width, height = img.size
    max_size = (128, 128)
    if width > height:
        height = int((max_size[0] / width) * height)
        width = max_size[0]
    else:
        width = int((max_size[1] / height) * width)
        height = max_size[1]
    image: LayoutElement = Image(
        Path(image_path),
        width=Decimal(width),
        height=Decimal(height),
        vertical_alignment=Alignment.MIDDLE
    )
    table_001 = FixedColumnWidthTable(number_of_columns=3, number_of_rows=4)
    table_001.add(Paragraph(" "))
    table_001.add(
        Paragraph("Invoice Statement", font="Helvetica-Bold", font_size=11, horizontal_alignment=Alignment.CENTERED)
    )
    table_001.add(TableCell(image, row_span=4))

    table_001.add(
        Paragraph(f"{account.name}", font="Helvetica-Bold", font_size=12)
    )
    table_001.add(Paragraph(" "))
    table_001.add(
        Paragraph(
            f"""
            {account.street1}
            {account.street2}
            {account.country}
            {account.phone}
            {account.email}
            HST# {account.hst}
            """, font="Helvetica", respect_newlines_in_text=True, font_size=8)
    )
    table_001.add(Paragraph(" "))
    table_001.add(Paragraph(" "))
    table_001.add(Paragraph(" "))

    table_001.no_borders()
    return table_001


def _build_invoice_information(user, invoices):
    customer = invoices.first().customer_id
    table_001 = FixedColumnWidthTable(number_of_rows=3, number_of_columns=3)
    table_001.add(Paragraph(" "))
    table_001.add(Paragraph(" "))
    table_001.add(Paragraph(" "))

    table_001.add(Paragraph("Billing Address", font="Helvetica-Bold", font_size=8))
    table_001.add(TableCell(
        Paragraph(
            f"Statement Date: {datetime.now().strftime('%m/%d/%Y %I:%M %p')}",
            font="Helvetica-Bold",
            font_size=9,
            horizontal_alignment=Alignment.RIGHT
        ),
        col_span=2

    )

    )
    table_001.add(Paragraph(
        f"""{customer.full_name}
        {customer.street1}
        {customer.street2}
        {customer.country}
        Phone: {customer.phone}
        Email: {customer.email}
        """, font="Helvetica", respect_newlines_in_text=True, font_size=8, horizontal_alignment=Alignment.LEFT,
        vertical_alignment=Alignment.TOP))
    table_001.add(Paragraph(" "))
    table_001.add(Paragraph(" "))
    table_001.set_padding_on_all_cells(Decimal(0), Decimal(0), Decimal(0), Decimal(0))
    table_001.no_borders()
    return table_001


def _build_invoice_detail_information(user, data):
    invoice = models.ModelsInvoice.objects.get(
        id=data["invoice_id"],
    )
    customer = invoice.customer_id
    crew = invoice.crew_id
    table_001 = FixedColumnWidthTable(number_of_rows=3, number_of_columns=3)
    table_002 = FixedColumnWidthTable(number_of_rows=6, number_of_columns=2)
    table_002.add(Paragraph("Invoice Number:", font="Helvetica-Bold", font_size=9,
                            horizontal_alignment=Alignment.RIGHT, ))
    table_002.add(Paragraph(f"{invoice.number}", font="Helvetica-Bold", font_size=9,
                            horizontal_alignment=Alignment.RIGHT, ))
    table_002.add(Paragraph("PO Number:", font="Helvetica-Bold", font_size=9,
                            horizontal_alignment=Alignment.RIGHT, ))
    table_002.add(Paragraph(f"{invoice.po}", font="Helvetica-Bold", font_size=9,
                            horizontal_alignment=Alignment.RIGHT, ))
    table_002.add(Paragraph(" "))
    table_002.add(Paragraph(" "))

    table_002.add(Paragraph("Work Order Close Date:", font="Helvetica-Bold", font_size=7,
                            horizontal_alignment=Alignment.RIGHT, ))
    table_002.add(Paragraph(f"{invoice.start_at.strftime('%d/%m/%y')}", font="Helvetica", font_size=7,
                            horizontal_alignment=Alignment.RIGHT, ))
    table_002.add(Paragraph("Invoice Date:", font="Helvetica-Bold", font_size=7,
                            horizontal_alignment=Alignment.RIGHT, ))
    table_002.add(Paragraph(f"{invoice.finished_at.strftime('%d/%m/%y')}", font="Helvetica", font_size=7,
                            horizontal_alignment=Alignment.RIGHT, ))
    table_002.add(Paragraph("Net Terms:", font="Helvetica-Bold", font_size=7,
                            horizontal_alignment=Alignment.RIGHT, ))
    table_002.add(Paragraph("DUE UPON RECEIPT", font="Helvetica", font_size=7,
                            horizontal_alignment=Alignment.RIGHT, ))
    table_002.no_borders()

    table_001.add(Paragraph(" "))
    table_001.add(Paragraph(" "))
    table_001.add(Paragraph(" "))

    table_001.add(Paragraph("Billing Address", font="Helvetica-Bold", font_size=8))
    table_001.add(
        Paragraph(
            "Service Address:",
            font="Helvetica-Bold",
            font_size=8,
        ))
    table_001.add(TableCell(table_002, row_span=2))
    te = 'Detail'
    table_001.add(Paragraph(
        f"""{customer.full_name}
        {customer.street1}
        {customer.street2}
        {customer.country}
        Phone: {customer.phone}
        Email: {customer.email}
        """, font="Helvetica", respect_newlines_in_text=True, font_size=8, horizontal_alignment=Alignment.LEFT,
        vertical_alignment=Alignment.TOP))
    table_001.add(Paragraph("Same as Billing Address", font="Helvetica", font_size=8))

    table_001.set_padding_on_all_cells(Decimal(0), Decimal(0), Decimal(0), Decimal(0))
    table_001.no_borders()
    return table_001


def _build_itemized_description_table(tax, invoices):
    if tax:
        table_001 = FixedColumnWidthTable(
            number_of_rows=len(invoices) + 7,
            number_of_columns=7,
        )
    else:
        table_001 = FixedColumnWidthTable(
            number_of_rows=len(invoices) + 5,
            number_of_columns=7,
        )

    for h in ["Invoice Number", "Invoice Date", "Due Date", "Invoice Status", "Total", "Paid", "Balance"]:
        table_001.add(
            TableCell(
                Paragraph(h, font="Helvetica-Bold", font_size=8)
            )
        )

    for row_number, item in enumerate(invoices):
        table_001.add(TableCell(Paragraph(item.number, font="Helvetica-Bold", font_size=8

                                          )))
        table_001.add(TableCell(Paragraph(str(item.start_at.strftime('%d/%m/%y')), font="Helvetica", font_size=8)))
        table_001.add(TableCell(Paragraph(str(item.finished_at.strftime('%d/%m/%y')), font="Helvetica", font_size=8)))
        table_001.add(
            TableCell(Paragraph(" " + str(item.status), font="Helvetica", font_size=8))
        )
        table_001.add(
            TableCell(Paragraph("$ " + str(item.total_sum), font="Helvetica", font_size=8))
        )
        table_001.add(
            TableCell(Paragraph("$ 0", font="Helvetica", font_size=8))
        )
        table_001.add(
            TableCell(Paragraph("$ " + str(item.total_sum), font="Helvetica", font_size=8))
        )

    # for row_number in range(2):
    for _ in range(0, 7):
        table_001.add(TableCell(Paragraph(" ", border_top=True)))

    # total
    subtotal: float = sum([x.total_sum for x in invoices])

    if tax:
        hst: float = (sum([x.total_sum for x in invoices]) * 13) / 100
        table_001.add(
            TableCell(
                Paragraph(
                    "Subtotal:",
                    font="Helvetica-Bold",
                    horizontal_alignment=Alignment.RIGHT,
                    font_size=8,
                    padding_top=5,
                ),
                col_span=6,
            )
        )
        table_001.add(
            TableCell(Paragraph(f"$ {subtotal}", font_size=8,
                                padding_top=5, horizontal_alignment=Alignment.LEFT))
        )

        table_001.add(
            TableCell(
                Paragraph(
                    "HST:",
                    font="Helvetica-Bold",
                    horizontal_alignment=Alignment.RIGHT,
                    font_size=8,
                    padding_top=5,
                ),
                col_span=6,
            )
        )
        table_001.add(
            TableCell(Paragraph(f"$ {hst}", font_size=8,
                                padding_top=5, horizontal_alignment=Alignment.LEFT))
        )

        table_001.add(
            TableCell(
                Paragraph(
                    "Total Due:",
                    font="Helvetica-Bold",
                    horizontal_alignment=Alignment.RIGHT,
                    font_size=8,
                    padding_top=5,
                ),
                col_span=6,
            )
        )
        table_001.add(
            TableCell(Paragraph(f"$ {hst + subtotal}", font_size=8,
                                padding_top=5, horizontal_alignment=Alignment.LEFT))
        )
    else:
        table_001.add(
            TableCell(
                Paragraph(
                    "Total Due:",
                    font="Helvetica-Bold",
                    horizontal_alignment=Alignment.RIGHT,
                    font_size=8,
                    padding_top=5,
                ),
                col_span=6,
            )
        )
        table_001.add(
            TableCell(Paragraph(f"$ {subtotal}", font_size=8,
                                padding_top=5, horizontal_alignment=Alignment.LEFT))
        )

    for _ in range(0, 7):
        table_001.add(TableCell(Paragraph(" ")))

    table_001.add(
        TableCell(
            Paragraph(
                """
                Comment: 
                Thank you for your business
                """,
                font_size=8,
                font="Helvetica",
                padding_top=5, respect_newlines_in_text=True
            ),
            col_span=7, )
    )

    table_001.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2), Decimal(2))
    table_001.no_borders()
    return table_001


def _build_itemized_detail_description_table(user, data):
    invoice = models.ModelsInvoice.objects.get(
        id=data["invoice_id"],
    )
    tax = data['tax']
    task_list = invoice.tasks.all()
    car = invoice.car_id
    crew = invoice.crew_id
    table_001 = FixedColumnWidthTable(
        number_of_rows=7 + len(task_list),
        number_of_columns=3,
    )
    table_001.add(
        TableCell(
            Paragraph(
                f"{car.model} ( Stock#: {car.stock}, VIN: {car.vin})",
                font="Helvetica",
                horizontal_alignment=Alignment.LEFT,
                font_size=12,
                padding_top=5,
            ),
            col_span=3,
        )
    )

    # table_001.add(Paragraph(" "))

    for task in task_list:
        table_001.add(
            TableCell(
                Paragraph(
                    f"{task.work}",
                    font="Helvetica-Bold",
                    horizontal_alignment=Alignment.CENTERED,
                    font_size=8,
                ),
                col_span=2,
            ))
        table_001.add(
            Paragraph(
                f"$ {task.payment}",
                font="Helvetica-Bold",
                horizontal_alignment=Alignment.RIGHT,
                font_size=8,
            )
        )

    for _ in range(0, 3):
        table_001.add(TableCell(Paragraph(" ")))

    table_001.add(
        TableCell(
            Paragraph(
                """
                Comment: 
                Thank you for your business
                """,
                font_size=8,
                font="Helvetica",
                padding_top=5, respect_newlines_in_text=True
            ),
            col_span=3, )
    )
    for _ in range(0, 3):
        table_001.add(TableCell(Paragraph(" ")))

    table_002 = FixedColumnWidthTable(number_of_rows=2, number_of_columns=2)
    table_002.add(Paragraph("Invoice Number:", font="Helvetica-Bold", font_size=9,
                            horizontal_alignment=Alignment.LEFT, ))
    table_002.add(Paragraph(f"{invoice.number}", font="Helvetica-Bold", font_size=9,
                            horizontal_alignment=Alignment.LEFT, ))
    table_002.add(Paragraph("PO Number:", font="Helvetica-Bold", font_size=9,
                            horizontal_alignment=Alignment.LEFT, ))
    table_002.add(Paragraph(f"{invoice.po}", font="Helvetica-Bold", font_size=9,
                            horizontal_alignment=Alignment.LEFT, ))

    table_002.no_borders()
    table_001.add(table_002)
    for _ in range(0, 5):
        table_001.add(TableCell(Paragraph(" ")))

    table_003 = FixedColumnWidthTable(number_of_rows=2, number_of_columns=2)
    table_003.add(Paragraph("Work completed by:", font="Helvetica-Bold", font_size=7,
                            horizontal_alignment=Alignment.LEFT, ))
    table_003.add(Paragraph(f"{crew.username.upper()}", font="Helvetica", font_size=7,
                            horizontal_alignment=Alignment.LEFT, ))
    table_003.add(Paragraph("Generated By:", font="Helvetica-Bold", font_size=7,
                            horizontal_alignment=Alignment.LEFT, ))
    table_003.add(Paragraph(f"{crew.username.upper()} {crew.lastname.upper()}", font="Helvetica", font_size=7,
                            horizontal_alignment=Alignment.LEFT, ))
    table_003.no_borders()
    table_001.add(table_003)
    table_001.add(Paragraph(" "))

    table_004 = FixedColumnWidthTable(number_of_rows=3, number_of_columns=3)
    if tax:

        hst: float = (invoice.total_sum * 13) / 100
        table_004.add(Paragraph("Sub Total:", font="Helvetica-Bold", font_size=8,
                                horizontal_alignment=Alignment.RIGHT, ))
        table_004.add(Paragraph(" "))
        table_004.add(Paragraph(f"${invoice.total_sum}", font="Helvetica", font_size=8,
                                horizontal_alignment=Alignment.LEFT, ))
        table_004.add(Paragraph("HST:", font="Helvetica-Bold", font_size=8,
                                horizontal_alignment=Alignment.RIGHT, ))
        table_004.add(Paragraph(" "))
        table_004.add(Paragraph(f"${hst}", font="Helvetica", font_size=8,
                                horizontal_alignment=Alignment.LEFT, ))
        table_004.add(Paragraph("Total:", font="Helvetica-Bold", font_size=8,
                                horizontal_alignment=Alignment.RIGHT, ))
        table_004.add(Paragraph(" "))
        table_004.add(Paragraph(f"${invoice.total_sum + hst}", font="Helvetica-Bold", font_size=8,
                                horizontal_alignment=Alignment.LEFT, ))
    else:
        table_004.add(Paragraph("Total:", font="Helvetica-Bold", font_size=8,
                                horizontal_alignment=Alignment.RIGHT, ))
        table_004.add(Paragraph(" "))
        table_004.add(Paragraph(f"${invoice.total_sum}", font="Helvetica", font_size=8,
                                horizontal_alignment=Alignment.LEFT, ))

        table_004.add(Paragraph(" "))
        table_004.add(Paragraph(" "))
        table_004.add(Paragraph(" "))

        table_004.add(Paragraph(" "))
        table_004.add(Paragraph(" "))
        table_004.add(Paragraph(" "))


    table_001.set_padding_on_all_cells(Decimal(0), Decimal(0), Decimal(0), Decimal(0))
    table_004.no_borders()
    table_001.add(table_004)

    table_001.set_padding_on_all_cells(Decimal(2), Decimal(2), Decimal(2), Decimal(2))
    table_001.no_borders()

    return table_001

@check_auth('default')
def generate_pdf_for_detailed_invoice(user, data):
    # Create document
    si = io.BytesIO()
    pdf = Document()

    # Add page
    page = Page()
    pdf.add_page(page)

    # create PageLayout
    page_layout: PageLayout = SingleColumnLayout(page)
    page_layout.vertical_margin = page.get_page_info().get_height() * Decimal(0.02)

    # Invoice information table
    page_layout.add(_build_invoice_information_head_detail(user, data))
    # page_layout.add(_build_invoice_information())
    page_layout.add(_build_invoice_detail_information(user, data))

    # Empty paragraph for spacing
    page_layout.add(Paragraph(" "))

    # Empty paragraph for spacing
    page_layout.add(Paragraph(" "))

    # Itemized description
    page_layout.add(
        _build_itemized_detail_description_table(user, data)
    )
    PDF.dumps(si, pdf)
    si.seek(0)
    invoice = models.ModelsInvoice.objects.get(
        id=data["invoice_id"],
    )

    filename = f'Invoice_{datetime.now().strftime("%H-%M_%d-%m-%y")}'
    if data['send']:
        customer = invoice.customer_id
        send_email_with_pdf_attachment(si, user, customer, filename, 'Invoice')
        return Response({'message': 'Email sent successfully'})
    else:
        response = HttpResponse(si.read(), content_type=('application/pdf'))
        response.headers['Content-Disposition'] = f"attachment; filename={filename}"
        response.headers["Content-type"] = "application/pdf"
        si.close()
        return response


@check_auth('default')
def generate_pdf_list_invoice(user, data):
    try:
        tz = timezone('UTC')
        start_date = datetime.strptime(data['start_date'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)
        end_date = datetime.strptime(data['end_date'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)
        tax = data['tax']
        invoices = models.ModelsInvoice.objects.filter(
            crew_id__account_id=user.account_id,
            customer_id_id=data['customer_id'],
            finished_at__range=(start_date, end_date)
        )

    except:
        return Response({
            'success': False,
        }, status=status.HTTP_400_BAD_REQUEST)

    # Create document
    si = io.BytesIO()
    pdf = Document()

    # Add page
    page = Page()
    pdf.add_page(page)

    # create PageLayout
    page_layout: PageLayout = SingleColumnLayout(page)
    page_layout.vertical_margin = page.get_page_info().get_height() * Decimal(0.02)

    # Invoice information table
    page_layout.add(_build_invoice_information_head(user, invoices))
    page_layout.add(_build_invoice_information(user, invoices))

    # Empty paragraph for spacing
    page_layout.add(Paragraph(" "))

    # Empty paragraph for spacing
    page_layout.add(Paragraph(" "))

    # Itemized description
    page_layout.add(
        _build_itemized_description_table(tax, invoices)
    )
    PDF.dumps(si, pdf)
    si.seek(0)

    filename = f'Invoice_statement_{datetime.now().strftime("%H-%M_%d-%m-%y")}'

    if data['send']:
        customer = invoices.first().customer_id
        send_email_with_pdf_attachment(si, user, customer, filename, 'Invoice Statement')
        return Response({'message': 'Email sent successfully'})
    else:
        response = HttpResponse(si.read(), content_type=('application/pdf'))
        response.headers['Content-Disposition'] = f"attachment; filename={filename}"
        response.headers["Content-type"] = "application/pdf"
        si.close()

        return response


@check_auth('admin')
def export_invoices_csv(user, data):
    invoices = query_invoice(user, data)
    filename = f'Invoices_{datetime.now().strftime("%H-%M_%d-%m-%y")}'
    output = io.StringIO()
    format_file = 'csv'
    csv_writer = csv.writer(output, delimiter=',')
    headers = [
        'InvoiceNO',
        'Customer',
        'InvoiceDate',
        'DueDate',
        'Item(Product/Service)',
        'ItemQuantity',
        'ItemRate',
        'ItemAmount',
        'ItemTaxCode',
        'ItemTaxAmount',
    ]
    data_csv = [headers]
    for inv in invoices:
        customer = inv.customer_id.full_name
        start_date = inv.start_at.strftime('%d/%m/%y')
        finished_date = inv.finished_at.strftime('%d/%m/%y')

        for i, task in enumerate(inv.tasks.all()):
            if i != 0:
                customer = ""
                start_date = ""
                finished_date = ""
            data_csv.append(
                [
                    inv.number,
                    customer,
                    start_date,
                    finished_date,
                    task.work,
                    "1",
                    task.payment,
                    task.payment,
                    "HST",
                    str((task.payment*13)/100)
                ]
            )
    csv_writer.writerows(data_csv)
    output.seek(0)
    response = HttpResponse(output.read(), content_type=('text/csv'))
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}.{format_file}"'
    response.headers["Content-type"] = "text/csv"
    output.close()
    return response


