# Generated by Django 3.0.7 on 2020-06-12 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cv', '0015_closematchsetmembership_core'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='closematchsetmembership',
            name='distance',
        ),
        migrations.AlterField(
            model_name='closematchsetmembership',
            name='core',
            field=models.BooleanField(db_index=True, default=True, help_text='Is this membership part of the core cluster or added in the second pass?'),
        ),
    ]