from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import render

def index(request):
    """
    Root view for the NeuroHire API.
    Redirects to the API documentation/browsable API.
    """
    api_endpoints = {
        "admin": "/admin/",
        "api_root": "/api/",
        "resume_upload": "/api/resumes/",
        "parsed_resumes": "/api/parsed-resumes/",
        "job_postings": "/api/jobs/",
        "candidate_matches": "/api/matches/",
        "candidate_profiles": "/api/candidates/",
        "social_profiles": "/api/social-profiles/",
        "api_auth": "/api-auth/",
        "api_token_auth": "/api-token-auth/"
    }
    
    return JsonResponse({
        "message": "Welcome to the NeuroHire API",
        "available_endpoints": api_endpoints
    })

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def handle_frontend_file_upload(request):
    """View to handle file uploads from the frontend."""
    """
    View to handle file uploads from the frontend.
    """
    try:
        if 'file' not in request.FILES:
            return Response({"success": False, "error": "No file provided"}, status=400)
        
        file = request.FILES['file']
        
        # Extract filename for better error messages
        filename = file.name
        
        # Process the file and save it using the Resume model
        from resume_parser.models import Resume
        resume = Resume.objects.create(file=file)
        
        # We'll rely completely on OCR and AI models for data extraction
        # Initialize variables that will be populated by the parsers
        text_content = ""
        contact_info = {}
        skills = []
        experience = []
        education = []
        scores = {}
        
        # Try to parse the resume with multiple fallback strategies
        try:
            # Try parsing with our available parsers
            try:
                # First try with our Integrated Parser which combines YOLO, OCR, and Gemini API
                from resume_parser.integrated_parser import IntegratedResumeParser
                parser = IntegratedResumeParser()
                parsed_data = parser.parse_resume(resume.file.path)
                print(f"Successfully parsed resume with IntegratedResumeParser: {filename}")
                
                # Mark as processed
                resume.processed = True
                resume.save()
            except ImportError as ie:
                print(f"IntegratedResumeParser import error: {ie}")
                # Fall back to EasyOCR parser
                try:
                    from resume_parser.easyocr_services import EasyOCRResumeParser
                    parser = EasyOCRResumeParser()
                    parsed_data = parser.parse_resume(resume.file.path)
                    print(f"Successfully parsed resume with EasyOCR: {filename}")
                    
                    # Mark as processed
                    resume.processed = True
                    resume.save()
                except Exception as easyocr_error:
                    print(f"EasyOCR error: {easyocr_error}")
                    # Fallback to Vision API if EasyOCR fails
                    try:
                        from resume_parser.vision_services import VisionResumeParser
                        parser = VisionResumeParser()
                        parsed_data = parser.parse_resume(resume.file.path)
                        print(f"Successfully parsed resume with Vision API: {filename}")
                    except Exception as vision_error:
                        print(f"Vision API error: {vision_error}")
                        # Return a meaningful error
                        return Response({
                            "success": False,
                            "error": "Could not parse resume with any available OCR services."
                        }, status=500)
            except Exception as integrated_error:
                print(f"IntegratedResumeParser error: {integrated_error}")
                # Fall back to EasyOCR parser
                try:
                    from resume_parser.easyocr_services import EasyOCRResumeParser
                    parser = EasyOCRResumeParser()
                    parsed_data = parser.parse_resume(resume.file.path)
                    print(f"Successfully parsed resume with EasyOCR: {filename}")
                    
                    # Mark as processed
                    resume.processed = True
                    resume.save()
                except Exception as easyocr_error:
                    print(f"EasyOCR error: {easyocr_error}")
                    # Fallback to Vision API if EasyOCR fails
                    try:
                        from resume_parser.vision_services import VisionResumeParser
                        parser = VisionResumeParser()
                        parsed_data = parser.parse_resume(resume.file.path)
                        print(f"Successfully parsed resume with Vision API: {filename}")
                    except Exception as vision_error:
                        print(f"Vision API error: {vision_error}")
                        # Return a meaningful error
                        return Response({
                            "success": False,
                            "error": "Could not parse resume with available OCR services."
                        }, status=500)
            
            # Extract data from parsed_data
            text_content = parsed_data.get('text_content', '')
            
            # Even if text is short, let's still try to proceed - don't error out here
            if not text_content or len(text_content) < 50:
                print(f"Warning: Extracted text is short or empty: '{text_content}'. Using available data anyway.")
                
            contact_info = parsed_data.get('contact_info', {})
            skills = parsed_data.get('skills', [])
            experience = parsed_data.get('experience', [])
            education = parsed_data.get('education', [])
            scores = parsed_data.get('scores', {})
            
            # Log the extracted information
            print(f"Extracted information from {filename}:")
            print(f"  Name: {contact_info.get('name')}")
            print(f"  Skills: {', '.join(skills[:5])}" if skills else "  No skills extracted")
            print(f"  Experience items: {len(experience)}")
            print(f"  Education items: {len(education)}")
            print(f"  AI Model scores:")
            print(f"    Competence: {scores.get('competence', 'N/A')}")
            print(f"    Experience: {scores.get('experience', 'N/A')}")
            print(f"    Formation: {scores.get('formation', 'N/A')}")
        except Exception as e:
            print(f"Resume parsing failed with error: {e}")
            # Return detailed error to client
            import traceback
            trace = traceback.format_exc()
            print(f"Traceback: {trace}")
            return Response({
                "success": False,
                "error": f"Failed to parse resume: {str(e)}"
            }, status=500)
        
        # Update resume text content
        resume.text_content = text_content
        resume.processed = True
        resume.save()
        
        # Create candidate profile from parsed resume
        try:
            from candidate_profiles.models import CandidateProfile
            
            # Get values for candidate profile
            name = contact_info.get('name', '')
            email = contact_info.get('email', '')
            phone = contact_info.get('phone', '')
            
            # Make sure we have some values to work with
            if not name:
                name = "Candidate " + str(resume.id)
                
            if not email:
                email = f"candidate{resume.id}@example.com"
                
            # Check if a candidate with this name already exists
            candidate, candidate_created = CandidateProfile.objects.get_or_create(
                name=name,
                defaults={
                    'email': email,
                    'phone': phone,
                    'skills': skills,
                    'experience_summary': "Has experience with " + ", ".join(skill for skill in skills[:3]) if skills else "Various technologies",
                    'education_summary': education[0].get('degree', 'Degree') + " from " + education[0].get('institution', 'University') if education else "University Degree"
                }
            )
            print(f"Candidate profile {'created' if candidate_created else 'updated'}: {candidate.name}")
        except Exception as e:
            print(f"Error creating candidate profile: {e}")
        
        # Create parsed resume object with whatever data we got
        from resume_parser.models import ParsedResume
        parsed_resume, created = ParsedResume.objects.update_or_create(
            resume=resume,
            defaults={
                'name': contact_info.get('name', ''),
                'email': contact_info.get('email', ''),
                'phone': contact_info.get('phone', ''),
                'skills': skills,
                'experience': experience,
                'education': education,
                'github_profile': contact_info.get('github'),
                'linkedin_profile': contact_info.get('linkedin'),
                'competence_score': scores.get('competence', 0.0),
                'experience_score': scores.get('experience', 0.0),
                'formation_score': scores.get('formation', 0.0)
            }
        )
    
        # Return the response
        return Response({
            "success": True,
            "fileName": file.name,
            "fileSize": file.size,
            "resumeId": resume.id,
            "parsedResumeId": parsed_resume.id,
            "candidateName": parsed_resume.name if parsed_resume.name else "Unknown",
            "extractedSkills": parsed_resume.skills if parsed_resume.skills else []
        })
    except Exception as e:
        import traceback
        print(f"Resume upload error: {e}")
        print(traceback.format_exc())
        return Response({
            "success": False,
            "error": f"An error occurred while processing the resume: {str(e)}"
        }, status=500)
