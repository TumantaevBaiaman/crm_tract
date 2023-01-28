import csv
import json
from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.postgres.fields import ArrayField
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import F, Value
from urllib.parse import urlencode
from django.conf import settings
from django.db.models import Sum
import  django.db.models as md
from pytz import timezone
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
import os
from datetime import datetime
from django.core.files.storage import default_storage
from django.http.request import QueryDict
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
from ..users.logic.logic import check_auth


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
    # start_date = datetime.strptime(data['start_date'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)
    # end_date = datetime.strptime(data['end_date'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)
    crew_id = data['crew_id'] if data['crew_id'] else None
    car_id = data['car_id'] if data['car_id'] else None
    customer_id = data['customer_id'] if data['customer_id'] else None
    number = data['number'] if data['number'] else None
    finished_at = data['finished_at'] if data['finished_at'] else None
    start_at = data['start_at'] if data['start_at'] else None
    page = data["page"] if data['page'] else 1
    page_size = data["page_size"] if data['page_size'] else 10

    invoices = models.ModelsInvoice.objects.all()

    if number is not None:
        invoices = invoices.filter(number=number)
    if crew_id is not None:
        invoices = invoices.filter(crew_id=crew_id)
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
    # )
    invoices_data = invoices.values('customer_id').annotate(
        name=F('customer_id__full_name'),
        invoices=Value(
            json.dumps(list(invoices.values()), cls=DjangoJSONEncoder),
            output_field=md.JSONField()
        ),
        total_sum=Sum('total_sum')
    )

    paginator = PageNumberPagination()
    paginator.page = page
    paginator.page_size = page_size
    paginated_data = paginator.paginate_queryset(invoices_data, request)
    total_sum = invoices.aggregate(Sum('total_sum'))
    response = paginator.get_paginated_response(paginated_data)
    response.data['Page_total_sum'] = total_sum
    # print(response.data)
    # response_data = response.data['results']
    # for item in response_data:
    #     invoices_json = json.loads(item['invoices'])
    #     item['invoices'] = invoices_json
    return response
    # result_page = paginator.paginate_queryset(invoices, request=request)
    # pk_list = [invoices.pk for invoices in result_page]
    # serializer = SerializerInvoice(result_page, many=True)
    # total_sum = models.ModelsInvoice.objects.filter(
    #     pk__in=pk_list
    # ).aggregate(Sum('total_sum'))
    # print(total_sum)
    # data_ = serializer.data
    # data_.append({'all_total_sum': total_sum['total_sum__sum']})
    # total_sum_current_page = page.aggregate(Sum('total_sum'))['total_sum__sum']
    # return paginator.get_paginated_response(invoices_data)


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
            'car': SerializerInvoice(invoice).data,
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

    image_path = os.path.join(settings.MEDIA_ROOT, url)
    with default_storage.open(image_path, 'rb') as f:
        img = IM.open(f)
        width, height = img.size
    if width > height:
        w = 128
        h = 80
    elif width < height:
        w = 80
        h = 128
    else:
        w = 128
        h = 128
    image: LayoutElement = Image(
        Path(image_path),
        width=Decimal(w),
        height=Decimal(h),
        horizontal_alignment=Alignment.LEFT
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
    if width > height:
        w = 128
        h = 80
    elif width < height:
        w = 80
        h = 128
    else:
        w = 128
        h = 128
    image: LayoutElement = Image(
        Path(image_path),
        width=Decimal(w),
        height=Decimal(h),
        horizontal_alignment=Alignment.LEFT
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

    response = HttpResponse(si.read(), content_type=('application/pdf'))
    name = f'Invoice_{datetime.now().strftime("%H-%M_%d-%m-%y")}'
    response.headers['Content-Disposition'] = f"attachment; filename={name}"
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

    response = HttpResponse(si.read(), content_type=('application/pdf'))
    name = f'Invoice_statement_{datetime.now().strftime("%H-%M_%d-%m-%y")}'
    response.headers['Content-Disposition'] = f"attachment; filename={name}"
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
    """
    response = HttpResponse(si.read(), content_type=('application/pdf'))
    name = f'Invoice_statement_{datetime.now().strftime("%H-%M_%d-%m-%y")}'
    response.headers['Content-Disposition'] = f"attachment; filename={name}"
    response.headers["Content-type"] = "application/pdf"
    si.close()
    """
    response = HttpResponse(output.read(), content_type=('text/csv'))
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}.{format_file}"'
    response.headers["Content-type"] = "text/csv"
    output.close()
    return response


