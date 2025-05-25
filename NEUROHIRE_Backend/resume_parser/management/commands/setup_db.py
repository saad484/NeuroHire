from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import connection

class Command(BaseCommand):
    help = 'Set up the initial database structure for NeuroHire'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting NeuroHire database setup...'))
        
        # Create superuser if none exists
        if not User.objects.filter(is_superuser=True).exists():
            self.stdout.write('Creating superuser...')
            User.objects.create_superuser(
                username='admin',
                email='admin@neurohire.com',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS('Superuser created successfully!'))
            self.stdout.write(self.style.WARNING('Username: admin, Password: admin123 - CHANGE THIS IN PRODUCTION!'))
        else:
            self.stdout.write('Superuser already exists, skipping...')
        
        # Check if tables are created correctly
        with connection.cursor() as cursor:
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            tables = [row[0] for row in cursor.fetchall()]
            
        expected_tables = [
            'resume_parser_resume',
            'resume_parser_parsedresume',
            'job_matching_jobposting',
            'job_matching_candidatematch',
            'candidate_profiles_candidateprofile',
            'candidate_profiles_socialprofile',
        ]
        
        missing_tables = [table for table in expected_tables if table not in tables]
        
        if missing_tables:
            self.stdout.write(self.style.WARNING(f'Missing tables: {", ".join(missing_tables)}'))
            self.stdout.write('Make sure to run migrations with: python manage.py migrate')
        else:
            self.stdout.write(self.style.SUCCESS('All expected tables exist in the database.'))
        
        self.stdout.write(self.style.SUCCESS('NeuroHire database setup completed!'))
