# Generated by Django 3.0.5 on 2020-05-09 13:03

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('classroom', '0003_auto_20200509_1821'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='assignmentsubmission',
            unique_together={('assignment_id', 'student_id')},
        ),
        migrations.AlterUniqueTogether(
            name='classroomstudents',
            unique_together={('classroom_id', 'student_id')},
        ),
        migrations.AlterUniqueTogether(
            name='joinrequests',
            unique_together={('classroom_id', 'student_id')},
        ),
    ]
