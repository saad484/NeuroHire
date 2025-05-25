from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import Resume, ParsedResume
from .serializers import ResumeSerializer, ParsedResumeSerializer
try:
    from .services import ResumeParser
except ImportError:
    # Fall back to simplified services if the full services are not available
    from .simplified_services import SimpleResumeParser as ResumeParser
import os

class ResumeViewSet(viewsets.ModelViewSet):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    permission_classes = [AllowAny]  # Allow unauthenticated access for demo purposes
    
    @action(detail=True, methods=['post'])
    def parse(self, request, pk=None):
        """Parse the resume and extract information"""
        resume = self.get_object()
        
        if resume.processed:
            return Response(
                {'detail': 'This resume has already been processed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get file path from media root
            file_path = resume.file.path
            
            # Parse resume
            parser = ResumeParser()
            parsed_data = parser.parse_resume(file_path)
            
            # Update resume text content
            resume.text_content = parsed_data['text_content']
            resume.processed = True
            resume.save()
            
            # Create or update parsed resume object
            parsed_resume, created = ParsedResume.objects.update_or_create(
                resume=resume,
                defaults={
                    'name': parsed_data['contact_info'].get('name'),
                    'email': parsed_data['contact_info'].get('email'),
                    'phone': parsed_data['contact_info'].get('phone'),
                    'skills': parsed_data['skills'],
                    'experience': parsed_data['experience'],
                    'education': parsed_data['education'],
                    'github_profile': parsed_data['contact_info'].get('github'),
                    'linkedin_profile': parsed_data['contact_info'].get('linkedin')
                }
            )
            
            # Return parsed data
            return Response({
                'id': parsed_resume.id,
                'parsed_data': parsed_data
            })
        except Exception as e:
            return Response(
                {'detail': f'Error parsing resume: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ParsedResumeViewSet(viewsets.ModelViewSet):
    queryset = ParsedResume.objects.all()
    serializer_class = ParsedResumeSerializer
    permission_classes = [AllowAny]  # Allow unauthenticated access for demo purposes
    
    def destroy(self, request, *args, **kwargs):
        """Override destroy to handle cascading deletion of resume files"""
        parsed_resume = self.get_object()
        parsed_resume_id = parsed_resume.id
        
        try:
            # Get related objects
            resume = None
            if hasattr(parsed_resume, 'resume'):
                resume = parsed_resume.resume
            
            # Delete in the correct order
            # 1. Get the file path before deleting the object if it exists
            file_path = None
            if resume and hasattr(resume, 'file'):
                try:
                    file_path = resume.file.path
                except Exception as e:
                    print(f"Error getting file path: {e}")
            
            # 2. Delete the ParsedResume object
            parsed_resume.delete()
            print(f"Deleted parsed resume {parsed_resume_id}")
            
            # 3. Delete the Resume object if it exists
            if resume:
                resume_id = resume.id
                resume.delete()
                print(f"Deleted resume {resume_id}")
                
                # 4. Delete the physical file if it exists
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
            
            return Response({
                'success': True,
                'message': f'Successfully deleted parsed resume {parsed_resume_id}'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            print(f"Error deleting parsed resume: {e}")
            print(traceback.format_exc())
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
