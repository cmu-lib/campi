# Generated by Django 3.0.7 on 2020-06-17 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cv', '0018_remove_closematchset_invalid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='closematchsetmembership',
            name='accepted',
        ),
        migrations.RemoveField(
            model_name='closematchsetmembership',
            name='invalid',
        ),
        migrations.AddField(
            model_name='closematchsetmembership',
            name='state',
            field=models.CharField(choices=[('n', 'Not yet reviewed'), ('a', 'Accepted'), ('r', 'Rejected'), ('o', 'Already matched in other set'), ('e', 'Explicitly excluded from any consideration by an editor')], db_index=True, default='n', help_text='Status of this membership (e.g. accepted, rejected)', max_length=1),
        ),
    ]
