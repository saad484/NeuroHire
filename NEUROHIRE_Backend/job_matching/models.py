from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class JobPosting(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    description = models.TextField()
    required_skills = models.JSONField(default=list)
    required_experience_years = models.IntegerField()
    education_level = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return f'{self.title} at {self.company}'

class CandidateMatch(models.Model):
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='matches')
    parsed_resume = models.ForeignKey('resume_parser.ParsedResume', on_delete=models.CASCADE)
    match_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    skills_match = models.JSONField()
    experience_match = models.FloatField()
    education_match = models.FloatField()
    github_score = models.FloatField(null=True, blank=True)
    linkedin_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-match_score']
    
    def __str__(self):
        return f'Match: {self.parsed_resume.name} - {self.job.title} ({self.match_score}%)'
# Create your models here.
