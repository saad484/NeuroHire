from rest_framework import serializers
from .models import Resume, ParsedResume

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ['id', 'file', 'uploaded_at', 'processed', 'text_content']
        read_only_fields = ['uploaded_at', 'processed', 'text_content']

class ParsedResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParsedResume
        fields = ['id', 'resume', 'name', 'email', 'phone', 'skills', 
                 'experience', 'education', 'github_profile', 'linkedin_profile']
        read_only_fields = ['id']
