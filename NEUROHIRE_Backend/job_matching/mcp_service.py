import os
import json
import requests
import google.generativeai as genai
from django.conf import settings

class ModelContextProtocol:
    """
    Model Context Protocol (MCP) service for analyzing social profiles
    and extracting relevant context for job matching
    """
    
    def __init__(self):
        # Initialize Gemini API for advanced context analysis
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        
    def analyze_github_profile(self, github_username):
        """
        Analyze a GitHub profile using MCP approach to extract:
        - Programming languages used
        - Project details and descriptions
        - Contribution activity and quality
        - Areas of expertise based on project content
        """
        if not github_username:
            return None
            
        try:
            # Use Gemini to gather information about the GitHub profile
            prompt = f"""Analyze the GitHub profile of user '{github_username}' and provide a detailed report. Include:

            1. Programming languages used (ranked by frequency)
            2. List of notable projects with descriptions
            3. Activity level assessment (low/medium/high/very high)
            4. Technical areas of expertise
            5. Quality assessment of repositories
            6. Open source contributions
            
            Return as JSON with these keys: languages, projects, activity_level, expertise, quality_assessment, open_source_contributions
            """
            
            response = self.model.generate_content(prompt)
            github_data = json.loads(response.text)
            
            # Additional validation and enrichment of data
            if 'projects' in github_data and github_data['projects']:
                # Further analyze each project for deeper insights
                for i, project in enumerate(github_data['projects']):
                    if isinstance(project, dict) and 'name' in project:
                        # Get deeper analysis of specific projects
                        project_prompt = f"""Analyze GitHub project '{project['name']}' by {github_username} in detail.
                        Focus on:
                        1. Technical complexity (1-10 scale)
                        2. Key technologies used
                        3. Software architecture patterns
                        4. Code quality indicators
                        
                        Return as JSON.
                        """
                        try:
                            project_response = self.model.generate_content(project_prompt)
                            project_analysis = json.loads(project_response.text)
                            github_data['projects'][i]['detailed_analysis'] = project_analysis
                        except Exception as e:
                            print(f"Error analyzing project {project['name']}: {e}")
                            
            return github_data
            
        except Exception as e:
            print(f"Error analyzing GitHub profile with MCP: {e}")
            return None
    
    def analyze_linkedin_profile(self, linkedin_username):
        """
        Analyze a LinkedIn profile using MCP approach to extract:
        - Current and past roles
        - Skills and endorsements
        - Education details
        - Certifications and achievements
        - Industry connections and influence
        """
        if not linkedin_username:
            return None
            
        try:
            # Use Gemini to gather information about the LinkedIn profile
            prompt = f"""Analyze the LinkedIn profile of user '{linkedin_username}' and provide a detailed report. Include:

            1. Current position and company
            2. Experience level assessment (entry/junior/mid/senior/executive)
            3. Past roles and responsibilities
            4. Industry and domain expertise
            5. Skills (technical and soft)
            6. Education background
            7. Certifications and achievements
            
            Return as JSON with these keys: current_position, company, experience_level, past_roles, industry, skills, education, certifications
            """
            
            response = self.model.generate_content(prompt)
            linkedin_data = json.loads(response.text)
            
            # Enrich with industry relevance analysis
            if 'industry' in linkedin_data and linkedin_data['industry']:
                industry_prompt = f"""Provide detailed analysis of the '{linkedin_data['industry']}' industry:
                1. Key technologies and skills in demand
                2. Current trends and challenges
                3. Market growth prospects
                4. Leading companies
                
                Return as JSON.
                """
                try:
                    industry_response = self.model.generate_content(industry_prompt)
                    industry_analysis = json.loads(industry_response.text)
                    linkedin_data['industry_analysis'] = industry_analysis
                except Exception as e:
                    print(f"Error analyzing industry: {e}")
            
            return linkedin_data
            
        except Exception as e:
            print(f"Error analyzing LinkedIn profile with MCP: {e}")
            return None
    
    def compare_project_to_job(self, project_data, job_requirements):
        """
        Compare a specific project with job requirements to determine relevance and skill match
        """
        if not project_data or not job_requirements:
            return 0, {}
            
        try:
            # Create a comprehensive comparison prompt
            project_json = json.dumps(project_data)
            job_json = json.dumps(job_requirements)
            
            prompt = f"""Compare this candidate's project:
            {project_json}
            
            With these job requirements:
            {job_json}
            
            Analyze:
            1. Technical skill alignment (0-100 score)
            2. Domain knowledge relevance (0-100 score)
            3. Project complexity vs job complexity (0-100 score)
            4. Specific matched skills
            5. Missing required skills
            
            Return as JSON with these keys: technical_score, domain_score, complexity_score, matched_skills, missing_skills, overall_score
            """
            
            response = self.model.generate_content(prompt)
            comparison_data = json.loads(response.text)
            
            # Calculate overall score if not provided
            if 'overall_score' not in comparison_data:
                weights = {
                    'technical_score': 0.5,
                    'domain_score': 0.3,
                    'complexity_score': 0.2
                }
                
                overall_score = sum(
                    comparison_data.get(key, 0) * weight 
                    for key, weight in weights.items()
                )
                
                comparison_data['overall_score'] = overall_score
                
            return comparison_data['overall_score'], comparison_data
            
        except Exception as e:
            print(f"Error comparing project to job with MCP: {e}")
            return 0, {}
    
    def create_comprehensive_profile(self, parsed_resume, github_data, linkedin_data):
        """
        Create a comprehensive candidate profile by combining resume data with GitHub and LinkedIn analysis
        """
        if not parsed_resume:
            return {}
            
        comprehensive_profile = {
            'basic_info': {
                'name': parsed_resume.name,
                'email': parsed_resume.email,
                'phone': parsed_resume.phone
            },
            'resume_skills': parsed_resume.skills,
            'resume_experience': parsed_resume.experience,
            'resume_education': parsed_resume.education,
            'github_profile': github_data if github_data else {},
            'linkedin_profile': linkedin_data if linkedin_data else {}
        }
        
        # Generate a consolidated skills list across all sources
        all_skills = set(parsed_resume.skills if parsed_resume.skills else [])
        
        if github_data and 'languages' in github_data:
            for lang in github_data['languages']:
                all_skills.add(lang)
                
        if github_data and 'expertise' in github_data:
            for expertise in github_data['expertise']:
                all_skills.add(expertise)
                
        if linkedin_data and 'skills' in linkedin_data:
            for skill in linkedin_data['skills']:
                all_skills.add(skill)
        
        comprehensive_profile['consolidated_skills'] = list(all_skills)
        
        # Calculate skill confidence based on verification across sources
        skill_confidence = {}
        for skill in all_skills:
            confidence = 0
            
            # Skill in resume
            if parsed_resume.skills and skill in parsed_resume.skills:
                confidence += 0.3
                
            # Skill in GitHub
            github_confirmed = False
            if github_data:
                if 'languages' in github_data and skill in github_data['languages']:
                    github_confirmed = True
                elif 'expertise' in github_data and skill in github_data['expertise']:
                    github_confirmed = True
                    
            if github_confirmed:
                confidence += 0.4
                
            # Skill in LinkedIn
            if linkedin_data and 'skills' in linkedin_data and skill in linkedin_data['skills']:
                confidence += 0.3
                
            skill_confidence[skill] = min(confidence, 1.0)  # Cap at 1.0
            
        comprehensive_profile['skill_confidence'] = skill_confidence
        
        return comprehensive_profile
    
    def analyze_job_match(self, comprehensive_profile, job_posting):
        """
        Perform comprehensive job matching analysis using MCP
        """
        if not comprehensive_profile or not job_posting:
            return 0, {}
            
        try:
            # Convert to JSON for Gemini prompt
            profile_json = json.dumps(comprehensive_profile)
            job_json = json.dumps({
                'title': job_posting.title,
                'company': job_posting.company,
                'description': job_posting.description,
                'required_skills': job_posting.required_skills,
                'required_experience_years': job_posting.required_experience_years,
                'education_level': job_posting.education_level
            })
            
            prompt = f"""As an expert recruiter, analyze this candidate's comprehensive profile against this job posting.
            
            Candidate Profile:
            {profile_json}
            
            Job Posting:
            {job_json}
            
            Provide a detailed analysis with:
            1. Skills match score (0-100)
            2. Experience match score (0-100)
            3. Education match score (0-100)
            4. GitHub projects relevance score (0-100)
            5. LinkedIn profile relevance score (0-100)
            6. Overall match score (0-100)
            7. Key strengths for this position
            8. Areas for improvement
            9. Specific project experiences that align with job requirements
            10. Detailed explanation of the match
            
            Return as JSON.
            """
            
            response = self.model.generate_content(prompt)
            match_analysis = json.loads(response.text)
            
            return match_analysis.get('overall_match_score', 0), match_analysis
            
        except Exception as e:
            print(f"Error analyzing job match with MCP: {e}")
            return 0, {}
