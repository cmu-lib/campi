# Generated by Django 3.0.7 on 2020-06-11 16:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('photograph', '0003_auto_20200608_1103'),
        ('cv', '0013_auto_20200611_1229'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='closematchset',
            unique_together={('close_match_run', 'representative_photograph')},
        ),
        migrations.RemoveField(
            model_name='closematchset',
            name='seed_photograph',
        ),
    ]
