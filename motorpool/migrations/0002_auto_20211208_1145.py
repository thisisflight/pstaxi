# Generated by Django 3.2.9 on 2021-12-08 08:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('motorpool', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='brand',
            options={'verbose_name': 'Бренд', 'verbose_name_plural': 'Бренды'},
        ),
        migrations.AlterModelTable(
            name='brand',
            table='brand',
        ),
        migrations.CreateModel(
            name='Auto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=15)),
                ('description', models.TextField(blank=True, default='', max_length=500)),
                ('year', models.PositiveSmallIntegerField(null=True)),
                ('auto_class', models.CharField(choices=[('e', 'economy'), ('c', 'comfort'), ('b', 'business')], default='e', max_length=1, null=True)),
                ('brand', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='motorpool.brand')),
            ],
            options={
                'verbose_name': 'Автомобиль',
                'verbose_name_plural': 'Автомобили',
                'db_table': 'auto',
            },
        ),
    ]