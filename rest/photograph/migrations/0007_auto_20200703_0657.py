# Generated by Django 3.0.7 on 2020-07-03 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photograph', '0006_auto_20200702_0739'),
    ]

    operations = [
        migrations.AddField(
            model_name='faceannotation',
            name='anger_likelihood',
            field=models.PositiveIntegerField(db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='faceannotation',
            name='blurred_likelihood',
            field=models.PositiveIntegerField(db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='faceannotation',
            name='detection_confidence',
            field=models.FloatField(db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='faceannotation',
            name='headwear_likelihood',
            field=models.PositiveIntegerField(db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='faceannotation',
            name='joy_likelihood',
            field=models.PositiveIntegerField(db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='faceannotation',
            name='sorrow_likelihood',
            field=models.PositiveIntegerField(db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='faceannotation',
            name='surprise_likelihood',
            field=models.PositiveIntegerField(db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='faceannotation',
            name='under_exposed_likelihood',
            field=models.PositiveIntegerField(db_index=True, null=True),
        ),
    ]
