# Generated by Django 4.1.3 on 2023-04-13 14:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModelsCustomer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.TextField(max_length=122)),
                ('full_name', models.CharField(max_length=50)),
                ('street1', models.CharField(blank=True, max_length=122)),
                ('street2', models.CharField(max_length=255)),
                ('country', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=255)),
                ('phone2', models.CharField(blank=True, max_length=255, null=True)),
                ('postal_code', models.CharField(max_length=255)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('deleted', models.BooleanField(default=False)),
                ('account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='account.modelsaccount')),
            ],
        ),
    ]
