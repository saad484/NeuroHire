from rest_framework import serializers
from django.contrib.auth.models import User
from .models import CandidateProfile, SocialProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']

class SocialProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialProfile
        fields = ['id', 'platform', 'profile_url', 'profile_data', 'last_updated']
        read_only_fields = ['id', 'last_updated']

class CandidateProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    social_profiles = SocialProfileSerializer(many=True, read_only=True)
    
    class Meta:
        model = CandidateProfile
        fields = ['id', 'user', 'parsed_resume', 'bio', 'profile_picture',
                 'current_position', 'location', 'social_profiles']
        read_only_fields = ['id']
