# Generated by Django 3.0.5 on 2020-05-19 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0010_auto_20200519_2231'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assignmentgrades',
            name='publish',
        ),
        migrations.AddField(
            model_name='assignment',
            name='publish_grades',
            field=models.BooleanField(default=False, verbose_name='publish'),
        ),
    ]
