from django.urls import path, include, re_path
from .views import *

urlpatterns = [
    re_path(r'^classrooms$', ClassCreateListAPIView.as_view()),
    re_path(r'^join_requests$', JoinClassAPIView.as_view()),

    re_path(r'^classrooms/(?P<pk>[0-9A-Za-z_\-]+)$', ClassRetriveUpdateDeleteAPIView.as_view()),
    re_path(r'^assignments/(?P<pk>[0-9]+)$', DownloadAssignmentFileView.as_view()),
    
    re_path(r'^classrooms/(?P<classroom>[0-9A-Za-z_\-]+)/assignments$', AssignmentCreateListAPIView.as_view()),
    re_path(r'^classrooms/(?P<classroom>[0-9A-Za-z_\-]+)/join_requests$', JoinRequestsListAPIView.as_view()),
    re_path(r'^classrooms/(?P<classroom>[0-9A-Za-z_\-]+)/reference_materials$', ReferenceMaterialCreateListAPIView.as_view()),
    re_path(r'^classrooms/(?P<classroom>[0-9A-Za-z_\-]+)/students$', ClassroomStudentsListAPIView.as_view()),
    re_path(r'^classrooms/(?P<classroom>[0-9A-Za-z_\-]+)/students/(?P<pk>[0-9]+)$', ClassroomStudentsRemoveAPIView.as_view()),

    
    re_path(r'^classrooms/(?P<classroom>[0-9A-Za-z_\-]+)/join_requests/(?P<pk>[0-9]+)$', JoinRequestAcceptRejectAPIView.as_view()),
    re_path(r'^classrooms/(?P<classroom>[0-9A-Za-z_\-]+)/assignments/(?P<pk>[0-9]+)$', AssignmentRetriveUpdateDeleteAPIView.as_view()),
    re_path(r'^classrooms/(?P<classroom>[0-9A-Za-z_\-]+)/reference_materials/(?P<pk>[0-9]+)$', ReferenceMaterialRetriveUpdateAPIView.as_view()),


    re_path(r'^classrooms/(?P<classroom>[0-9A-Za-z_\-]+)/assignments/(?P<assignment>[0-9]+)/submissions$', AssignmentSubmissionCreateListAPIView.as_view()),
    re_path(r'^classrooms/(?P<classroom>[0-9A-Za-z_\-]+)/assignments/(?P<assignment>[0-9]+)/submissions/(?P<pk>[0-9]+)$', AssignmentSubmissionUpdateAPIView.as_view()),
]
