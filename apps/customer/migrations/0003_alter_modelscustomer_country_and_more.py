# Generated by Django 4.1.3 on 2023-08-20 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modelscustomer',
            name='country',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='modelscustomer',
            name='email',
            field=models.TextField(blank=True, max_length=122, null=True),
        ),
        migrations.AlterField(
            model_name='modelscustomer',
            name='full_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='modelscustomer',
            name='phone',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='modelscustomer',
            name='postal_code',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='modelscustomer',
            name='street1',
            field=models.CharField(blank=True, max_length=122, null=True),
        ),
        migrations.AlterField(
            model_name='modelscustomer',
            name='street2',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]