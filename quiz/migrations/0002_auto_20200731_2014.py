# Generated by Django 3.0.5 on 2020-07-31 14:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('quiz', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='enable_quiz_for_all',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='QuizStudentPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allowed_to_attempt', models.BooleanField(default=False)),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='permissions', to='quiz.Quiz')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quizzes_allowed', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('quiz', 'student')},
            },
        ),
    ]