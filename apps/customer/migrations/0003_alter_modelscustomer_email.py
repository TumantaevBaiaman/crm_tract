# Generated by Django 4.1.3 on 2023-01-30 05:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modelscustomer',
            name='email',
            field=models.TextField(max_length=122),
        ),
    ]