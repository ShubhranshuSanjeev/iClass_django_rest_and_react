from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, username, is_student, is_teacher, **extra_fields):
        if not email:
            raise ValueError(_("The email value must be set"))
        if not username:
            raise ValueError(_("Username must be provided"))
        if not password:
            raise ValueError(_("Password must be set"))

        email   = self.mormalize_email(email)
        user    = self.model(email=email, username=username, is_student=is_student, is_teacher=is_teacher, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)

        return user

    def create_user(self, email, password=None, username=None, is_student=False, is_teacher=False, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return _create_user(email, password, username, is_student, is_teacher, **extra_fields)
    
    def create_superuser(self, email, password=None, username=None, is_student=False, is_teacher=False, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_superuser') is False:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self._create_user(email, password, username, is_student, is_teacher, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    username            = models.CharField(_("username") ,max_length = 30, primary_key=True)
    email               = models.EmailField(_("email"),max_length=60, unique=True)
    first_name          = models.CharField(_("first name"), max_length=30, blank=True)
    last_name           = models.CharField(_("last name"), max_length=30, blank=True)
    is_student          = models.BooleanField(_("student"), default=False)
    is_teacher          = models.BooleanField(_("teacher"), default=False)
    avatar              = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    date_joined         = models.DateTimeField(verbose_name="Date Joined", auto_now_add=True)
    last_login          = models.DateTimeField(verbose_name="Last Login", auto_now=True)
    is_active           = models.BooleanField(verbose_name="Active", default=True)

    objects = CustomUserManager()

    USERNAME_FIELD      = "email"
    REQUIRED_FIELDS     = []

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
    
    def get_full_name(self):
        full_name = ' '.join(self.first_name, self.last_name)
        return full_name

    def get_short_name(self):
        return self.first_name

    def get_classrooms(self):
        if self.is_teacher:
            return self.taking_classes.all()
        else:
            return self.attending_classes.get_related('room_number','course_name', 'teacher_id').all()

class Teacher(models.Model):
    user = models.OneToOneField(User, related_name="teacher", on_delete=models.CASCADE)

    def get_user(self):
        return self.user.username

class Student(models.Model):
    user = models.OneToOneField(User, related_name="student", on_delete=models.CASCADE)

    def get_user(self):
        return self.user.username