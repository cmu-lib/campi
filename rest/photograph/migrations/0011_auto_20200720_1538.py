# Generated by Django 3.0.7 on 2020-07-20 19:38

import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('photograph', '0010_remove_photolabelannotation_topicality'),
    ]

    operations = [
        migrations.CreateModel(
            name='TextAnnotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, default='', help_text='Short readable label', max_length=400)),
                ('sequence', models.PositiveIntegerField(db_index=True, help_text='Sequence within a set')),
                ('x', models.PositiveIntegerField(help_text='Number of pixels from the left side of the image')),
                ('width', models.PositiveIntegerField(help_text='Width of the region in pixes')),
                ('y', models.PositiveIntegerField(help_text='Number of pixels from the top side of the image')),
                ('height', models.PositiveIntegerField(help_text='Height of the region in pixes')),
            ],
        ),
        migrations.AddField(
            model_name='photograph',
            name='image_search_text',
            field=django.contrib.postgres.search.SearchVectorField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='photograph',
            name='image_text',
            field=models.TextField(default='', help_text='Any text recognized in the image by Google Cloud Vision', null=True),
        ),
        migrations.AddIndex(
            model_name='photograph',
            index=django.contrib.postgres.indexes.GinIndex(fields=['image_search_text'], name='photograph__image_s_1af42c_gin'),
        ),
        migrations.AddField(
            model_name='textannotation',
            name='photograph',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='textannotation', to='photograph.Photograph'),
        ),
        migrations.AlterUniqueTogether(
            name='textannotation',
            unique_together={('photograph', 'sequence')},
        ),
    ]
