from django.db import models
from django.utils.translation import ugettext_lazy as _
from accounts.models import Student, Teacher

class Classroom(models.Model):
    classroom_id            = models.UUIDField(_("classroom id"),primary_key=True, editable=False)
    room_number             = models.IntegerField(_("room number"),blank=True)
    course_name             = models.CharField(_("course name"), max_length=60, blank=False)
    teacher_id              = models.ForeignKey(Teacher, related_name="taking_classes", on_delete=models.CASCADE)
    student_id              = models.ManyToManyField(Student, related_name="attending_classes")
    
    class Meta:
        verbose_name = _("Classroom")
        verbose_name_plural = _("Classrooms")

    def __str__(self):
        return self.course_name
    
    def get_teacher(self):
        return self.teacher_id
    
    def get_sudents(self):
        return self.student_id.all()
    
    def get_assignments(self):
        return self.assignments.all()
    
    def get_notes(self):
        return self.notes.all()
    
    def get_assignment_submissions(self):
        return self.get_assignment_submissions.all()

class Assignment(models.Model):
    classroom_id            = models.ForeignKey(Classroom, related_name="assignments", on_delete=models.CASCADE)
    description             = models.CharField(_("description"), max_length=75, blank=False)
    question                = models.FileField(upload_to='assignment_questions/', blank=False)
    max_marks               = models.IntegerField(default=100)

    def get_submissions(self):
        return self.assignment_submissions.all()

class Note(models.Model):
    classroom_id            = models.ForeignKey(Classroom, related_name="notes", on_delete=models.CASCADE)
    description             = models.CharField(max_length=100, blank=False)
    file                    = models.FileField(upload_to="notes/", blank=False)

class AssignmentSubmission(models.Model):
    assignment_id           = models.ForeignKey(Assignment, related_name="assignment_submissions", on_delete=models.CASCADE)
    student_id              = models.ForeignKey(Student, related_name="submitted_solutions", on_delete=models.CASCADE)
    solution_file           = models.FileField(upload_to="assignment_submission", blank=False)
    marks                   = models.PositiveIntegerField()
