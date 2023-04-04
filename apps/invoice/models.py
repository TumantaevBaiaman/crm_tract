import random

from django.db import models
from typing import Dict, List, Tuple
import uuid
from django.utils import timezone
from datetime import datetime

from apps.account.models import ModelsAccount
from apps.cars.models import ModelsCars
from apps.users.models import ModelsUser
from apps.customer.models import ModelsCustomer
from apps.task.models import ModelsTask


def dict_to_choices(dict: Dict[str, str]) -> List[Tuple[str, str]]:
    return [
        (key, value)
        for key, value in dict.items()
    ]


class ModelsInvoice(models.Model):
    STATUSES = {
        'draft': 'Draft',
        'final': 'Final',
        'cancel': 'Cancel',
    }

    STATUS_CHOICES = dict_to_choices(STATUSES)
    number = models.CharField(max_length=255, null=True)
    crew_id = models.ForeignKey(ModelsUser, on_delete=models.CASCADE)
    car_id = models.ForeignKey(ModelsCars, on_delete=models.CASCADE)
    customer_id = models.ForeignKey(ModelsCustomer, on_delete=models.CASCADE)
    account = models.ForeignKey(ModelsAccount, on_delete=models.CASCADE)
    tasks = models.ManyToManyField(ModelsTask, verbose_name='task', blank=True)
    status = models.CharField('Status', choices=STATUS_CHOICES, default='draft', max_length=100)
    description = models.TextField(null=True, blank=True)
    total_sum = models.IntegerField(null=True, blank=True)
    start_at = models.DateTimeField('Start_date', default=timezone.now)
    finished_at = models.DateTimeField('End_date', default=timezone.now,  null=True, blank=True)

    def __str__(self):
        return f"{self.crew_id}, {self.car_id}"

    def save(self, *args, **kwargs):
        if self.pk:
            if len(str(self.pk)) > 6:
                temp_number = str(self.pk)
            else:
                temp_number = f'{self.pk:06}'
            self.number = str(datetime.now().year) + '-' + temp_number
        super().save(*args, **kwargs)

