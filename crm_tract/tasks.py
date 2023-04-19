from celery.loaders import app
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework.response import Response

from celery import shared_task

from apps.account.models import Transaction, ModelsAccount, ModelsSatusAccount


@shared_task
def send_monthly_invoice():
    today = timezone.now()
    for account in ModelsAccount.objects.filter(status__name='active'):
        if account.last_invoice_month is None:
            account.last_invoice_month = today
            account.save()
        else:
            last_invoice_month = account.last_invoice_month
            delta = today - last_invoice_month
            if 33 > delta.days >= 30:
                next_invoice_month = last_invoice_month.replace(month=last_invoice_month.month + 1)
                subject = f"Monthly invoice for {account.name}"
                message = f"Please pay your monthly invoice for subscription."
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [account.email]
                send_mail(subject, message, from_email, recipient_list)
                transaction = Transaction.objects.create(
                    account=account,
                    paid=False,
                )
                account.last_invoice_month = next_invoice_month
                account.save()
            elif delta.days >= 33:
                account.status = ModelsSatusAccount.objects.get(name='inactive')
                account.save()

    return Response({'detail': 'Monthly invoices sent'})
