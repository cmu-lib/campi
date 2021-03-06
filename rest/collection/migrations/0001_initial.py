# Generated by Django 3.0.5 on 2020-05-21 19:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, default='', help_text='Short readable label', max_length=400)),
                ('description', models.TextField(blank=True, help_text='Descriptive notes')),
                ('date_start', models.DateField()),
                ('date_end', models.DateField()),
                ('user_last_modified', models.ForeignKey(editable=False, help_text='Last modified by user', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='jobs_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Directory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, default='', help_text='Short readable label', max_length=400)),
                ('description', models.TextField(blank=True, help_text='Descriptive notes')),
                ('parent_directory', models.ForeignKey(help_text='The immediate parent of this directory', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_directories', to='collection.Directory')),
                ('user_last_modified', models.ForeignKey(editable=False, help_text='Last modified by user', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='directorys_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
