# Generated by Django 4.1.3 on 2022-11-21 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ModelsCars',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('vin', models.CharField(max_length=55)),
                ('model', models.CharField(max_length=255)),
                ('image', models.ImageField(upload_to='')),
                ('create_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Car',
            },
        ),
    ]