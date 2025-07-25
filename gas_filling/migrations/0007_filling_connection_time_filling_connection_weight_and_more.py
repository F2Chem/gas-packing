# Generated by Django 4.2.7 on 2025-07-15 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gas_filling', '0006_alter_cylinder_barcodeid_alter_cylinder_tare_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='filling',
            name='connection_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='filling',
            name='connection_weight',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='filling',
            name='pulled_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='filling',
            name='pulled_weight',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
