# Generated by Django 3.0.7 on 2020-07-20 17:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cv', '0023_delete_closematchrunconsidered'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResNet18',
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
