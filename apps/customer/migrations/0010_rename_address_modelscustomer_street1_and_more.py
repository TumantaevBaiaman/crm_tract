# Generated by Django 4.1.3 on 2023-01-21 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0009_modelscustomer_deleted'),
    ]

    operations = [
        migrations.RenameField(
            model_name='modelscustomer',
            old_name='address',
            new_name='street1',
        ),
        migrations.AddField(
            model_name='modelscustomer',
            name='country',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='modelscustomer',
            name='phone',
            field=models.CharField(default=11, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='modelscustomer',
            name='street2',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]