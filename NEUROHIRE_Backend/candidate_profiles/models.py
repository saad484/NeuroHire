from django.db import models
from django.contrib.auth.models import User

class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    parsed_resume = models.OneToOneField('resume_parser.ParsedResume', on_delete=models.SET_NULL, null=True, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    current_position = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f'Profile of {self.user.get_full_name() or self.user.username}'

class SocialProfile(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='social_profiles')
    platform = models.CharField(max_length=50)  # e.g., 'github', 'linkedin'
    profile_url = models.URLField()
    profile_data = models.JSONField(null=True, blank=True)  # Cached profile data
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['candidate', 'platform']
    
    def __str__(self):
        return f'{self.platform} profile of {self.candidate.user.username}'
# Create your models here.
