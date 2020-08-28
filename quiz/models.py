from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from classroom.models import (
    Classroom,
    ClassroomStudents
)

class Quiz(models.Model):
    classroom               = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="quizzes")
    owner                   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name                    = models.CharField(max_length=255)
    duration                = models.DurationField(verbose_name=_("quiz duration"))
    start_time              = models.DateTimeField(verbose_name=_("quiz start time"))
    end_time                = models.DateTimeField(verbose_name=_("quiz end time"))
    publish_results         = models.BooleanField(default=False)
    enable_quiz_for_all     = models.BooleanField(default=False)
    max_attempts            = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    def get_questions(self):
        return self.questions.all()

    def get_submissions(self):
        pass

class QuizStudentPermission(models.Model):
    quiz                = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="permissions")
    student             = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quizzes_allowed")
    allowed_to_attempt  = models.BooleanField(default=False)

    class Meta:
        unique_together = ('quiz', 'student')

class Question(models.Model):
    quiz            = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text            = models.CharField(max_length = 1000)
    points          = models.PositiveIntegerField()
    negative_mark   = models.IntegerField(default=0)

    def __str__(self):
        return self.text

    def get_answers(self):
        return self.answers.all()

class Answer(models.Model):
    question        = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    text            = models.CharField(max_length = 550)
    is_correct      = models.BooleanField(default=False)

class Sitting(models.Model):
    student         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quiz_attempts")
    quiz            = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="submissions")
    score           = models.IntegerField(default=0)
    submission_time = models.DateTimeField()

    def get_student_answers(self):
        return self.answers.all()


class StudentAnswer(models.Model):
    sitting         = models.ForeignKey(Sitting, on_delete=models.CASCADE, related_name="answers")
    question        = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer          = models.ForeignKey(Answer, on_delete=models.CASCADE)
    submission_time = models.DateTimeField()
