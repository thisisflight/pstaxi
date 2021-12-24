# Generated by Django 3.2.9 on 2021-12-08 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('motorpool', '0002_auto_20211208_1145'),
    ]

    operations = [
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name_plural': 'Опции',
            },
        ),
        migrations.AddField(
            model_name='auto',
            name='options',
            field=models.ManyToManyField(to='motorpool.Option'),
        ),
    ]