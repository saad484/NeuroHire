"""
URL configuration for neurohire_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import index, handle_frontend_file_upload

# Import views from apps
from resume_parser.views import ResumeViewSet, ParsedResumeViewSet
from job_matching.views import JobPostingViewSet, CandidateMatchViewSet
from candidate_profiles.views import CandidateProfileViewSet, SocialProfileViewSet

# Set up the API router
router = DefaultRouter()
router.register(r'resumes', ResumeViewSet)
router.register(r'parsed-resumes', ParsedResumeViewSet)
router.register(r'jobs', JobPostingViewSet)
router.register(r'matches', CandidateMatchViewSet)
router.register(r'candidates', CandidateProfileViewSet)
router.register(r'social-profiles', SocialProfileViewSet)

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', obtain_auth_token),
    path('api/upload-resume/', handle_frontend_file_upload, name='upload-resume'),
]

# Add media URL handling
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
