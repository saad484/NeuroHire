from rest_framework import serializers
from .models import JobPosting, CandidateMatch

class JobPostingSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosting
        fields = ['id', 'title', 'company', 'description', 'required_skills',
                 'required_experience_years', 'education_level', 'created_at', 'active']
        read_only_fields = ['created_at']

class CandidateMatchSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    candidate_name = serializers.CharField(source='parsed_resume.name', read_only=True)
    
    class Meta:
        model = CandidateMatch
        fields = ['id', 'job', 'job_title', 'parsed_resume', 'candidate_name',
                 'match_score', 'skills_match', 'experience_match', 'education_match',
                 'github_score', 'linkedin_score', 'created_at']
        read_only_fields = ['id', 'created_at', 'match_score', 'skills_match',
                           'experience_match', 'education_match', 'github_score',
                           'linkedin_score']
