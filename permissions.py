from rest_framework import permissions

'''
Custom permission for making a view accessible 
only to the user whose rolw has been set as teacher.
'''
class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_teacher

'''
Custom permission to allow only a teacher to 
create new classrooms
'''
class DoesTeachClass(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.username == obj.teacher_id.user.username

class EitherTeachesorAttends(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return 

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_student

class HasCreatedAssignment(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj in request.user.teacher.owns_assignment

class HasCreatedNote(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj in request.user.teacher.owns_notes