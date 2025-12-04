from django.contrib import admin
from django.views.generic import TemplateView
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/", include("chats.urls")),
    
    # catch-all → serve Next.js index.html
    re_path(r"^(?:.*)/?$", TemplateView.as_view(template_name="static_frontend/index.html")),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
