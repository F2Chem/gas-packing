# Generated by Django 4.2.21 on 2025-07-16 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gas_filling', '0008_rename_tare_cylinder_heel_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cylinder_size',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='fill_size',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='num_of_cylinders',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='products',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
