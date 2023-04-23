from django.core.mail import send_mail
from django.utils import timezone
from celery import shared_task
from decouple import config
from apps.account.models import Transaction, ModelsAccount, ModelsSatusAccount
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)

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
                from_email = config('DJANGO_SUPERUSER_EMAIL')
                recipient_list = [account.email]
                send_mail(subject, message, from_email, recipient_list)
                transaction = Transaction.objects.create(
                    account=account,
                    paid=False,
                )
                transaction.save()
                account.last_invoice_month = next_invoice_month
                account.save()
            elif delta.days >= 33:
                account.status = ModelsSatusAccount.objects.get(name='inactive')
                account.save()

    return {'detail': 'Monthly invoices sent'}


@shared_task
def sample_task():
    logger.info("The sample task just ran.")