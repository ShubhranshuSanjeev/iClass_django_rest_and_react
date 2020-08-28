from django.contrib import admin
from django.urls import path, include, re_path
import accounts.api.urls
import classroom.api.urls
import quiz.api.urls
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    re_path(r'', include(accounts.api.urls)),
    re_path(r'', include(classroom.api.urls)),
    re_path(r'', include(quiz.api.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
