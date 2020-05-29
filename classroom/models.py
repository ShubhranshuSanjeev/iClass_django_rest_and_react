from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

def upload_assignment_file(instance, filename):
  print(instance.id)
  return "assignments/{classroom}/{filename}".format(
    classroom=str(instance.classroom_id.id),
    filename="Assignment"+str(instance.id)
  )
def upload_notes_file(instance, filename):
	return "notes/{classroom}/{filename}".format(
            classroom=str(instance.classroom_id.id),
            filename="ReferenceMaterial"+str(instance.id)
        )
def upload_submission_file(instance, filename):  
    return "submissions/{classroom}/{filename}".format(
        classroom=str(instance.assignment_id.classroom_id.id),
        filename="Submission"+str(instance.id)
    )

class Classroom(models.Model):
  id                    = models.UUIDField(_("classroom id"), primary_key=True, editable=False)
  room_number           = models.IntegerField(_("room number"),blank=True)
  course_name           = models.CharField(_("course name"), max_length=60, blank=False)
  teacher_id            = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="teaching_classrooms", on_delete=models.CASCADE)
  joining_permission    = models.BooleanField(_("joining permission"), default=True)

  class Meta:
    verbose_name = _("Classroom")
    verbose_name_plural = _("Classrooms")

  def __str__(self):
    return self.course_name
  
  def get_teacher(self):
    return self.teacher

  def get_sudents(self):
    return self.classroom_students.all()
  
  def get_assignments(self):
    return self.assignments.all()
  
  def get_notes(self):
    return self.reference_materials.all()
  
  def get_assignment_submissions(self):
    return self.assignment_submissions.all()
  
  def get_pending_join_requests(self):
    return self.pending_requests.all()

class ClassroomStudents(models.Model):
  classroom_id  = models.ForeignKey(Classroom, related_name="students", on_delete=models.CASCADE)
  student_id    = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="joined_classrooms", on_delete=models.CASCADE)

  class Meta:
    unique_together = (('classroom_id', 'student_id'), )

class JoinRequests(models.Model):
  classroom_id  = models.ForeignKey(Classroom, related_name='pending_requests', on_delete=models.CASCADE)
  student_id    = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='join_requests',on_delete=models.CASCADE)

  class Meta:
    unique_together = (('classroom_id', 'student_id'), )

class Assignment(models.Model):
  classroom_id    = models.ForeignKey(Classroom, related_name="assignments", on_delete=models.CASCADE)
  teacher         = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owns_assignment", on_delete=models.CASCADE)
  description     = models.CharField(_("description"), max_length=75, blank=False)
  file            = models.FileField(upload_to=upload_assignment_file, blank=False)
  deadline        = models.DateField(_("deadline"), blank=True)
  max_marks       = models.IntegerField(default=100)
  publish_grades  = models.BooleanField(verbose_name=_('publish'),default=False)

  def get_submissions(self):
    return self.assignment_submissions.all()

class ReferenceMaterial(models.Model):
  classroom_id    = models.ForeignKey(Classroom, related_name="reference_materials", on_delete=models.CASCADE)
  teacher_id      = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owns_reference_material", on_delete=models.CASCADE)
  description     = models.CharField(max_length=100, blank=False)
  file            = models.FileField(upload_to=upload_notes_file, blank=False)

class AssignmentSubmission(models.Model):
  assignment_id   = models.ForeignKey(Assignment, related_name="assignment_submissions", on_delete=models.CASCADE)
  student_id      = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owns_solution", on_delete=models.CASCADE)
  file            = models.FileField(upload_to=upload_submission_file, blank=False)
  marks           = models.PositiveIntegerField(default=0)

  class Meta:
    unique_together = (('assignment_id', 'student_id'),)