# Generated by Django 3.0.7 on 2020-06-09 20:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cv', '0009_auto_20200609_1050'),
    ]

    operations = [
        migrations.CreateModel(
            name='BitonalInceptionV3',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('cv.pytorchmodel',),
        ),
        migrations.CreateModel(
            name='ColorInceptionV3',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('cv.pytorchmodel',),
        ),
        migrations.CreateModel(
            name='GrayInceptionV3',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('cv.pytorchmodel',),
        ),
    ]