"""
Simplified resume parser service that works without requiring all AI dependencies.
This is a temporary placeholder until the full AI services can be installed.
"""

import os
import re
from django.conf import settings

class SimpleResumeParser:
    """A simplified resume parser without AI dependencies"""
    
    def __init__(self):
        pass
    
    def extract_text_from_pdf(self, pdf_path):
        """Simplified text extraction (returns placeholder text)"""
        # In the full implementation, this would use pdf2image and OCR
        return f"Extracted text from {os.path.basename(pdf_path)}"
    
    def extract_text_from_image(self, image_path):
        """Simplified image text extraction (returns placeholder text)"""
        # In the full implementation, this would use Google Vision API
        return f"Extracted text from image {os.path.basename(image_path)}"
    
    def extract_contact_info(self, text):
        """Extract basic contact information using regex patterns"""
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        linkedin_pattern = r'linkedin\.com/\S+'
        github_pattern = r'github\.com/\S+'
        
        contact_info = {
            'email': re.findall(email_pattern, text),
            'phone': re.findall(phone_pattern, text),
            'linkedin': re.findall(linkedin_pattern, text),
            'github': re.findall(github_pattern, text)
        }
        
        # Take first match for each field if exists
        return {k: v[0] if v else None for k, v in contact_info.items()}
    
    def parse_resume(self, file_path):
        """Simplified resume parsing that returns placeholder data"""
        # Determine file type and extract text
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            text = self.extract_text_from_pdf(file_path)
        elif file_ext in ['.jpg', '.jpeg', '.png']:
            text = self.extract_text_from_image(file_path)
        else:
            text = f"Content of {os.path.basename(file_path)}"
        
        # Placeholder data
        parsed_data = {
            'text_content': text,
            'contact_info': {
                'email': 'candidate@example.com',
                'phone': '123-456-7890',
                'linkedin': 'linkedin.com/in/candidate',
                'github': 'github.com/candidate'
            },
            'skills': ['Python', 'JavaScript', 'Machine Learning', 'Django'],
            'experience': [
                {
                    'title': 'Software Engineer',
                    'company': 'Example Corp',
                    'start_date': '2020-01',
                    'end_date': '2023-01',
                    'description': 'Worked on various software projects'
                }
            ],
            'education': [
                {
                    'degree': 'Bachelor of Science in Computer Science',
                    'institution': 'Example University',
                    'start_date': '2016-09',
                    'end_date': '2020-05',
                    'field': 'Computer Science'
                }
            ],
            'social_analysis': {}
        }
        
        # Try to extract real contact info if possible
        contact_info = self.extract_contact_info(text)
        if any(contact_info.values()):
            parsed_data['contact_info'].update({k: v for k, v in contact_info.items() if v})
        
        return parsed_data
