# Generated by Django 3.0.7 on 2020-07-15 23:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('photograph', '0009_photolabel_photolabelannotation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='photolabelannotation',
            name='topicality',
        ),
    ]
