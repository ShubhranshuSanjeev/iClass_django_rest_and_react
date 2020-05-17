from django.contrib import admin
from django.urls import path, include, re_path
import accounts.api.urls
import classroom.api.urls
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'', include(accounts.api.urls)),
    re_path(r'', include(classroom.api.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
