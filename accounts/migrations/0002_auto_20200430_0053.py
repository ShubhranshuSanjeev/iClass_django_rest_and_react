# Generated by Django 3.0.5 on 2020-04-29 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=30, primary_key=True, serialize=False, verbose_name='username'),
        ),
    ]
