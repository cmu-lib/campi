# Generated by Django 3.0.7 on 2020-06-19 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cv', '0019_auto_20200617_1711'),
    ]

    operations = [
        migrations.AddField(
            model_name='closematchsetmembership',
            name='user_added',
            field=models.BooleanField(db_index=True, default=False, help_text='Was this match manually added by a user?'),
        ),
        migrations.AlterField(
            model_name='closematchsetmembership',
            name='distance',
            field=models.FloatField(db_index=True, help_text='Cosine distance from the first membership added to this set', null=True),
        ),
    ]