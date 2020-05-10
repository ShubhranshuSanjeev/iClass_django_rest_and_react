from django.contrib import admin
from django.urls import path, include, re_path
import accounts.api.urls
import classroom.api.urls

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'', include(accounts.api.urls)),
    re_path(r'', include(classroom.api.urls)),
]
