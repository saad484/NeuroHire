import os
from django.core.management.base import BaseCommand
from django.db import transaction
from candidate_profiles.models import CandidateProfile, SocialProfile
from resume_parser.models import ParsedResume, Resume
from django.conf import settings


class Command(BaseCommand):
    help = 'Clears all candidate data from the database to allow for fresh testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--keep-files',
            action='store_true',
            help='Keep uploaded resume files',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        # Clear all SocialProfiles
        social_count = SocialProfile.objects.count()
        SocialProfile.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {social_count} social profiles'))

        # Clear all CandidateProfiles
        candidate_count = CandidateProfile.objects.count()
        CandidateProfile.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {candidate_count} candidate profiles'))

        # Get the count of ParsedResumes
        parsed_count = ParsedResume.objects.count()
        
        # Clear ParsedResumes
        ParsedResume.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {parsed_count} parsed resumes'))

        # Get count of Resumes
        resume_count = Resume.objects.count()
        
        # Handle Resume deletion
        if not options['keep_files']:
            # Get all resume file paths before deleting
            resume_files = [resume.file.path for resume in Resume.objects.all() if hasattr(resume.file, 'path')]
            
            # Delete Resume objects
            Resume.objects.all().delete()
            
            # Delete the actual files
            for file_path in resume_files:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        self.stdout.write(f'Deleted file: {file_path}')
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Could not delete file {file_path}: {e}'))
                    
            self.stdout.write(self.style.SUCCESS(f'Deleted {resume_count} resumes and their files'))
        else:
            # Just mark resumes as unprocessed without deleting
            Resume.objects.update(processed=False, text_content='')
            self.stdout.write(self.style.SUCCESS(f'Reset {resume_count} resumes (kept files)'))

        self.stdout.write(self.style.SUCCESS('Successfully cleared all candidate data!'))
