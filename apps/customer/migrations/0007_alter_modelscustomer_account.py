# Generated by Django 4.1.3 on 2022-12-21 07:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_alter_modelsaccount_status'),
        ('customer', '0006_modelscustomer_account'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modelscustomer',
            name='account',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='account.modelsaccount'),
            preserve_default=False,
        ),
    ]
