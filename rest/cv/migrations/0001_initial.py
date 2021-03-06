# Generated by Django 3.0.6 on 2020-05-29 14:14

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('photograph', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PyTorchModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(help_text='Unique short readable label', max_length=400, unique=True)),
                ('description', models.TextField(blank=True, help_text='Descriptive notes')),
                ('n_dimensions', models.PositiveIntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Embedding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('array', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), size=None)),
                ('photograph', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='embeddings', to='photograph.Photograph')),
                ('pytorch_model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='embeddings', to='cv.PyTorchModel')),
            ],
            options={
                'ordering': ['pytorch_model'],
                'unique_together': {('pytorch_model', 'photograph')},
            },
        ),
        migrations.CreateModel(
            name='AnnoyIdx',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('n_trees', models.PositiveIntegerField()),
                ('index_file', models.FilePathField(blank=True, null=True, path='/vol/cv/indices', unique=True)),
                ('pytorch_model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='annoyidx_ann_indices', to='cv.PyTorchModel')),
            ],
        ),
        migrations.CreateModel(
            name='IndexEmbedding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence', models.PositiveIntegerField(db_index=True, help_text='Sequence within a set')),
                ('annoy_idx', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='indexed_embeddings', to='cv.AnnoyIdx')),
                ('embedding', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='indexed_embeddings', to='cv.Embedding')),
            ],
            options={
                'unique_together': {('annoy_idx', 'embedding', 'sequence')},
            },
        ),
    ]
