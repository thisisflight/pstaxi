# Generated by Django 3.2.9 on 2021-12-22 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('motorpool', '0009_alter_vehiclepassport_auto'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='slug',
            field=models.SlugField(blank=True, default='', max_length=210),
        ),
    ]
