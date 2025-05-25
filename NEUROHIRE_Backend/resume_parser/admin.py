from django.contrib import admin
from .models import Resume, ParsedResume

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('id', 'uploaded_at', 'processed')
    list_filter = ('processed',)
    search_fields = ('text_content',)

@admin.register(ParsedResume)
class ParsedResumeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'github_profile', 'linkedin_profile')
    search_fields = ('name', 'email', 'skills')
    readonly_fields = ('skills', 'experience', 'education')
