import os
import pytesseract
from PIL import Image
import pdf2image
import io
import re
import json
import numpy as np
from google.cloud import vision
from django.conf import settings
import torch
import google.generativeai as genai

class ResumeParser:
    def __init__(self):
        self.vision_client = vision.ImageAnnotatorClient()
        # Load the AI models
        self.competence_model = torch.load(settings.AI_MODELS['COMPETENCE_MODEL_PATH'])
        self.experience_model = torch.load(settings.AI_MODELS['EXPERIENCE_MODEL_PATH'])
        self.formation_model = torch.load(settings.AI_MODELS['FORMATION_MODEL_PATH'])
        
        # Initialize Gemini API for enhanced text analysis
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.gemini_model = genai.GenerativeModel('gemini-pro')
    
    def extract_text_from_image(self, image_path):
        """Extract text from image using Google Cloud Vision API"""
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        response = self.vision_client.document_text_detection(image=image)
        
        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))
        
        return response.full_text_annotation.text
    
    def convert_pdf_to_images(self, pdf_path):
        """Convert PDF to images"""
        return pdf2image.convert_from_path(pdf_path)
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF using OCR"""
        images = self.convert_pdf_to_images(pdf_path)
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image)
        return text
    
    def extract_contact_info(self, text):
        """Enhanced extraction of contact information using both regex and Gemini"""
        # First pass with regex patterns
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        linkedin_pattern = r'(?:linkedin\.com|linked\.in)[/\\](?:in[/\\])?[\w-]+'
        github_pattern = r'(?:github\.com|git\.io)[/\\][\w-]+'
        website_pattern = r'(?:https?://)?(?:www\.)?[\w-]+\.[a-z]{2,}(?:/[^\s]*)?'
        
        contact_info = {
            'email': re.findall(email_pattern, text),
            'phone': re.findall(phone_pattern, text),
            'linkedin': re.findall(linkedin_pattern, text),
            'github': re.findall(github_pattern, text),
            'website': re.findall(website_pattern, text)
        }
        
        # Second pass with Gemini for anything missed by regex
        prompt = f"""Extract all contact information from this text. Look specifically for:
        1. Email addresses
        2. Phone numbers
        3. LinkedIn profiles (any format, including shortened URLs)
        4. GitHub profiles (any format)
        5. Personal websites
        6. Other social media profiles (Twitter/X, Instagram, etc.)
        
        Return as JSON with keys: email, phone, linkedin, github, website, other_social.
        Text: {text[:4000]}"""
        
        try:
            response = self.gemini_model.generate_content(prompt)
            gemini_results = json.loads(response.text)
            
            # Merge results, prioritizing regex findings
            for key in contact_info:
                if not contact_info[key] and key in gemini_results and gemini_results[key]:
                    contact_info[key] = gemini_results[key]
            
            # Add any additional social profiles found by Gemini
            if 'other_social' in gemini_results and gemini_results['other_social']:
                contact_info['other_social'] = gemini_results['other_social']
        except Exception as e:
            print(f"Error in Gemini contact extraction: {e}")
        
        # Take first match for each field if exists
        return {k: v[0] if isinstance(v, list) and v else v for k, v in contact_info.items()}
    
    def extract_sections(self, text):
        """Extract different sections from the resume"""
        # Use the trained models to identify sections
        sections = {
            'skills': self.extract_skills(text),
            'experience': self.extract_experience(text),
            'education': self.extract_education(text)
        }
        return sections
    
    def extract_skills(self, text):
        """Extract skills using the competence model"""
        # Direct model inference based on your pre-trained model
        # Your model likely returns detection coordinates and confidence scores
        with torch.no_grad():
            results = self.competence_model(text)  # Assuming text or converted image is the input
        
        # Extract skills from the detected areas based on model's output format
        skills = []
        
        # If the direct model extraction fails, fallback to Gemini
        if not skills:
            try:
                prompt = f"Extract all technical and professional skills from this text. Return as a JSON list. Text: {text[:4000]}"
                response = self.gemini_model.generate_content(prompt)
                skills = json.loads(response.text)
            except Exception as e:
                print(f"Error in Gemini skills extraction: {e}")
        
        return skills
    
    def extract_experience(self, text):
        """Extract work experience using the experience model"""
        # Direct model inference with your pre-trained model
        with torch.no_grad():
            results = self.experience_model(text)  # Assumes text input or image conversion
        
        # Process the experience sections detected by your model
        experiences = []
        
        # Fallback to Gemini if needed
        if not experiences:
            try:
                prompt = """Extract all work experience entries from this text. For each job, include:
                1. Job title
                2. Company name
                3. Start date
                4. End date
                5. Duration (in years if possible)
                6. Key responsibilities or achievements
                
                Return as a JSON list of objects. Text: {text[:4000]}"""
                response = self.gemini_model.generate_content(prompt)
                experiences = json.loads(response.text)
            except Exception as e:
                print(f"Error in Gemini experience extraction: {e}")
        
        return experiences
    
    def extract_education(self, text):
        """Extract education using the formation model"""
        # Use your pre-trained formation model
        with torch.no_grad():
            results = self.formation_model(text)  # Assumes appropriate input format
        
        # Process model outputs to extract education information
        education = []
        
        # Fallback to Gemini if needed
        if not education:
            try:
                prompt = """Extract all education entries from this text. For each entry, include:
                1. Degree/certification name
                2. Institution name
                3. Start date
                4. End date
                5. Field of study
                6. Any notable achievements
                
                Return as a JSON list of objects. Text: {text[:4000]}"""
                response = self.gemini_model.generate_content(prompt)
                education = json.loads(response.text)
            except Exception as e:
                print(f"Error in Gemini education extraction: {e}")
        
        return education
    
    def analyze_social_profiles(self, profiles):
        """Analyze extracted social profiles for additional information"""
        social_data = {}
        
        # Analyze GitHub profile if available
        if 'github' in profiles and profiles['github']:
            try:
                github_username = profiles['github'].split('/')[-1]
                prompt = f"""Find information about GitHub user {github_username}. Include:
                1. Programming languages used
                2. Notable projects
                3. Activity level
                4. Areas of expertise
                
                Return as JSON."""
                response = self.gemini_model.generate_content(prompt)
                social_data['github_analysis'] = json.loads(response.text)
            except Exception as e:
                print(f"Error analyzing GitHub profile: {e}")
        
        # Analyze LinkedIn profile if available
        if 'linkedin' in profiles and profiles['linkedin']:
            try:
                linkedin_path = profiles['linkedin'].split('/')[-1]
                prompt = f"""Find information about LinkedIn user with profile ID {linkedin_path}. Include:
                1. Current position
                2. Company
                3. Experience level
                4. Industry
                5. Skills
                
                Return as JSON."""
                response = self.gemini_model.generate_content(prompt)
                social_data['linkedin_analysis'] = json.loads(response.text)
            except Exception as e:
                print(f"Error analyzing LinkedIn profile: {e}")
        
        return social_data
    
    def parse_resume(self, file_path):
        """Main method to parse resume with enhanced social profile analysis"""
        # Determine file type and extract text
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            text = self.extract_text_from_pdf(file_path)
        elif file_ext in ['.jpg', '.jpeg', '.png']:
            text = self.extract_text_from_image(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        # Extract information
        contact_info = self.extract_contact_info(text)
        sections = self.extract_sections(text)
        
        # Analyze social profiles
        social_analysis = self.analyze_social_profiles(contact_info)
        
        # Combine all extracted information
        parsed_data = {
            'text_content': text,
            'contact_info': contact_info,
            'skills': sections['skills'],
            'experience': sections['experience'],
            'education': sections['education'],
            'social_analysis': social_analysis
        }
        
        return parsed_data
