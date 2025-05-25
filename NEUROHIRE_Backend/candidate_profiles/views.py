import os
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import CandidateProfile, SocialProfile
from .serializers import CandidateProfileSerializer, SocialProfileSerializer, UserSerializer
try:
    from .rag_service import RAGService
    # Initialize RAG service as a singleton
    rag_service = RAGService()
except ImportError:
    # Fall back to simplified RAG service
    from .simplified_rag_service import SimpleRAGService
    rag_service = SimpleRAGService()

# Import MCP with fallback to simplified version
try:
    from job_matching.mcp_service import ModelContextProtocol
except ImportError:
    # Simple placeholder for MCP
    class SimpleModelContextProtocol:
        def analyze_github_profile(self, username):
            return {'languages': ['Python', 'JavaScript'], 'projects': ['Project1', 'Project2']}
            
        def analyze_linkedin_profile(self, username):
            return {'position': 'Software Engineer', 'company': 'Example Corp'}
    
    ModelContextProtocol = SimpleModelContextProtocol

class CandidateProfileViewSet(viewsets.ModelViewSet):
    queryset = CandidateProfile.objects.all()
    serializer_class = CandidateProfileSerializer
    permission_classes = [AllowAny]  # Allow unauthenticated access for demo purposes
    
    @action(detail=True, methods=['get'])
    def social_profiles(self, request, pk=None):
        """Get all social profiles for a candidate"""
        candidate = self.get_object()
        social_profiles = candidate.social_profiles.all()
        serializer = SocialProfileSerializer(social_profiles, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_social_profile(self, request, pk=None):
        """Add a social profile to a candidate"""
        candidate = self.get_object()
        
        serializer = SocialProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(candidate=candidate)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def analyze_social_profiles(self, request, pk=None):
        """Analyze the candidate's social profiles using MCP"""
        candidate = self.get_object()
        
        # Check if candidate has a parsed resume
        if not hasattr(candidate, 'parsed_resume') or not candidate.parsed_resume:
            return Response(
                {'detail': 'Candidate does not have a parsed resume.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get social profiles
        social_profiles = candidate.social_profiles.all()
        
        # Initialize MCP service
        mcp_service = ModelContextProtocol()
        
        analysis_results = {}
        
        # Analyze each social profile
        for profile in social_profiles:
            if profile.platform.lower() == 'github':
                github_username = profile.profile_url.split('/')[-1]
                github_data = mcp_service.analyze_github_profile(github_username)
                if github_data:
                    analysis_results['github'] = github_data
                    
                    # Update profile data in database
                    profile.profile_data = github_data
                    profile.save()
                    
            elif profile.platform.lower() == 'linkedin':
                linkedin_username = profile.profile_url.split('/')[-1]
                linkedin_data = mcp_service.analyze_linkedin_profile(linkedin_username)
                if linkedin_data:
                    analysis_results['linkedin'] = linkedin_data
                    
                    # Update profile data in database
                    profile.profile_data = linkedin_data
                    profile.save()
        
        return Response({
            'candidate_id': candidate.id,
            'candidate_name': candidate.user.get_full_name() or candidate.user.username,
            'analysis_results': analysis_results
        })
    
    @action(detail=True, methods=['post'])
    def chat(self, request, pk=None):
        """Chat with the RAG system about this candidate"""
        candidate = self.get_object()
        
        # Validate request data
        if 'query' not in request.data:
            return Response(
                {'detail': 'Query parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        query = request.data['query']
        conversation_history = request.data.get('conversation_history', [])
        
        # Generate response using RAG
        response = rag_service.generate_response(candidate, query, conversation_history)
        
        return Response({
            'candidate_id': candidate.id,
            'query': query,
            'response': response,
            # Update conversation history with this exchange
            'conversation_history': conversation_history + [
                {'role': 'user', 'content': query},
                {'role': 'assistant', 'content': response}
            ]
        })
        
    def destroy(self, request, *args, **kwargs):
        """Override destroy method to handle cascading deletion"""
        candidate = self.get_object()
        candidate_id = candidate.id
        
        try:
            from resume_parser.models import ParsedResume, Resume
            
            # Get the related data
            # Check if candidate has a parsed resume relation
            parsed_resume = None
            resume = None
            
            try:
                # Get parsed resume from candidate if it exists
                if hasattr(candidate, 'parsed_resume') and candidate.parsed_resume:
                    parsed_resume = candidate.parsed_resume
                    # Get the original resume file if it exists
                    if hasattr(parsed_resume, 'resume'):
                        resume = parsed_resume.resume
            except Exception as e:
                print(f"Error getting parsed resume: {e}")
            
            # Delete in the correct order to maintain referential integrity
            # 1. Delete all social profiles
            social_profiles = SocialProfile.objects.filter(candidate=candidate)
            social_count = social_profiles.count()
            social_profiles.delete()
            print(f"Deleted {social_count} social profiles")
            
            # 2. Delete the candidate profile
            candidate.delete()
            print(f"Deleted candidate profile {candidate_id}")
            
            # 3. Handle parsed resume deletion separately if we have its ID
            if parsed_resume:
                parsed_resume_id = parsed_resume.id
                parsed_resume.delete()
                print(f"Deleted parsed resume {parsed_resume_id}")
            
            # 4. Handle resume file deletion separately if we have its ID
            if resume:
                # Get the file path before deleting the object
                try:
                    file_path = resume.file.path
                except Exception:
                    file_path = None
                    
                resume_id = resume.id
                resume.delete()
                print(f"Deleted resume {resume_id}")
                
                # Delete the actual file
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
            
            return Response({
                'success': True,
                'message': f'Successfully deleted candidate {candidate_id}'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            return Response({
                'success': False,
                'error': f'Failed to delete candidate: {str(e)}',
                'traceback': traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SocialProfileViewSet(viewsets.ModelViewSet):
    queryset = SocialProfile.objects.all()
    serializer_class = SocialProfileSerializer
    permission_classes = [AllowAny]  # Allow unauthenticated access for demo purposes
    
    @action(detail=True, methods=['post'])
    def refresh_data(self, request, pk=None):
        """Refresh the social profile data using MCP"""
        profile = self.get_object()
        
        # Initialize MCP service
        mcp_service = ModelContextProtocol()
        
        if profile.platform.lower() == 'github':
            github_username = profile.profile_url.split('/')[-1]
            profile_data = mcp_service.analyze_github_profile(github_username)
        elif profile.platform.lower() == 'linkedin':
            linkedin_username = profile.profile_url.split('/')[-1]
            profile_data = mcp_service.analyze_linkedin_profile(linkedin_username)
        else:
            return Response(
                {'detail': f'Analysis not supported for platform: {profile.platform}'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if profile_data:
            # Update profile data
            profile.profile_data = profile_data
            profile.save()
            
            return Response({
                'profile_id': profile.id,
                'platform': profile.platform,
                'profile_data': profile_data
            })
        else:
            return Response(
                {'detail': 'Failed to retrieve profile data.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
