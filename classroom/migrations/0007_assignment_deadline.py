# Generated by Django 3.0.5 on 2020-05-15 07:54

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0006_auto_20200509_2026'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='deadline',
            field=models.DateField(blank=True, default=django.utils.timezone.now, verbose_name='deadline'),
            preserve_default=False,
        ),
    ]
