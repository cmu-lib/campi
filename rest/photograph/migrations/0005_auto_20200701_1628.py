# Generated by Django 3.0.7 on 2020-07-01 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photograph', '0004_auto_20200701_1539'),
    ]

    operations = [
        migrations.AddField(
            model_name='photograph',
            name='height',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='photograph',
            name='width',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
