# Generated by Django 3.0.4 on 2020-03-28 19:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=1000, unique=True)),
                ('parent_collection', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_collections', to='collection.Collection')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
