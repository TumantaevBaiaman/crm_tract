# Generated by Django 4.1.3 on 2023-01-22 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0008_modelsinvoice_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='modelsinvoice',
            name='po',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='modelsinvoice',
            name='number',
            field=models.CharField(max_length=255, null=True),
        ),
    ]