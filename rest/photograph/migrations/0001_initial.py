# Generated by Django 3.0.5 on 2020-04-26 18:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('collection', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Photograph',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, default='', max_length=1000)),
                ('description', models.TextField(blank=True, max_length=10000)),
                ('image_path', models.CharField(editable=False, help_text='Base path for the image on the IIIF server', max_length=2000, unique=True)),
                ('original_server_path', models.CharField(editable=False, help_text='The original path and filename from the archives server', max_length=2000, unique=True)),
                ('date_taken_early', models.DateField(db_index=True, help_text='Earliest possible date the original photograph was taken')),
                ('date_taken_late', models.DateField(db_index=True, help_text='Latest possible date the original photograph was taken')),
                ('digitized_date', models.DateTimeField(db_index=True, help_text='Creation date of the original TIF file on the archives server')),
                ('all_directories', models.ManyToManyField(help_text='All ancestor directories. Provided for faster filtering.', related_name='all_photographs', to='collection.Collection')),
                ('directory', models.ForeignKey(help_text='Parent directory', on_delete=django.db.models.deletion.CASCADE, related_name='immediate_photographs', to='collection.Collection')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, db_index=True, help_text='Date created (automatically recorded)')),
                ('last_updated', models.DateField(auto_now=True, db_index=True, help_text='Date last modified (automatically recorded)')),
                ('x_min', models.PositiveIntegerField()),
                ('x_max', models.PositiveIntegerField()),
                ('y_max', models.PositiveIntegerField()),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='annotations', to=settings.AUTH_USER_MODEL)),
                ('photograph', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='annotations', to='photograph.Photograph')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
