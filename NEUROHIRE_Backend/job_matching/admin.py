from django.contrib import admin
from .models import JobPosting, CandidateMatch

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'company', 'required_experience_years', 'education_level', 'active', 'created_at')
    list_filter = ('active', 'education_level')
    search_fields = ('title', 'company', 'description')
    readonly_fields = ('created_at',)

@admin.register(CandidateMatch)
class CandidateMatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'job', 'parsed_resume', 'match_score', 'experience_match', 'education_match', 'created_at')
    list_filter = ('job',)
    search_fields = ('job__title', 'parsed_resume__name')
    readonly_fields = ('skills_match', 'created_at')
    ordering = ('-match_score',)
