from django.db import models

class Resume(models.Model):
    file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    text_content = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f'Resume {self.id} - {self.uploaded_at}'

class ParsedResume(models.Model):
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name='parsed_data')
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    skills = models.JSONField(default=list, blank=True)
    experience = models.JSONField(default=list, blank=True)
    education = models.JSONField(default=list, blank=True)
    github_profile = models.URLField(null=True, blank=True)
    linkedin_profile = models.URLField(null=True, blank=True)
    
    # AI model scores
    competence_score = models.FloatField(default=0.0)
    experience_score = models.FloatField(default=0.0)
    formation_score = models.FloatField(default=0.0)
    
    def __str__(self):
        return f'Parsed Resume - {self.name or self.id}'

# Create your models here.
