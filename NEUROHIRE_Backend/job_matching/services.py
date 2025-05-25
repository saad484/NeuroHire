import os
import json
import logging
import numpy as np
import re
from django.conf import settings

# Import AI configuration
from .ai_config import is_genai_available
if is_genai_available:
    import google.generativeai as genai
    import torch
else:
    # Create placeholder for torch if not available
    class TorchPlaceholder:
        @staticmethod
        def load(path):
            return None
    torch = TorchPlaceholder()

class JobMatcher:
    def __init__(self):
        # Logger for tracking initialization
        self.logger = logging.getLogger(__name__)
        self.is_ai_available = is_genai_available
        self.model = None
        self.competence_model = None
        self.experience_model = None
        self.formation_model = None
        
        # Try to initialize Gemini and load models
        try:
            if self.is_ai_available:
                # Gemini model initialization
                self.model = genai.GenerativeModel('gemini-2.0-flash')
                self.logger.info("Gemini model initialized successfully")
                
                # Try to load the AI models for MCP
                try:
                    if hasattr(settings, 'AI_MODELS'):
                        self.competence_model = torch.load(settings.AI_MODELS.get('COMPETENCE_MODEL_PATH'))
                        self.experience_model = torch.load(settings.AI_MODELS.get('EXPERIENCE_MODEL_PATH'))
                        self.formation_model = torch.load(settings.AI_MODELS.get('FORMATION_MODEL_PATH'))
                        self.logger.info("AI models loaded successfully")
                    else:
                        self.logger.warning("AI_MODELS setting not found. Some advanced features may be unavailable.")
                except Exception as e:
                    self.logger.warning(f"Failed to load AI models: {str(e)}. Some advanced features may be unavailable.")
        except Exception as e:
            self.logger.warning(f"Failed to initialize AI components: {str(e)}. Using simplified matching.")
            self.is_ai_available = False
    
    def calculate_skills_match(self, required_skills, candidate_skills):
        """Calculate the match percentage between required and candidate skills"""
        if not required_skills or not candidate_skills:
            return 0, {}
        
        matches = {}
        total_required = len(required_skills)
        matched = 0
        
        for req_skill in required_skills:
            req_skill_lower = req_skill.lower()
            best_match = None
            best_score = 0
            
            for cand_skill in candidate_skills:
                cand_skill_lower = cand_skill.lower()
                # Simple string matching for now, could be enhanced with semantic similarity
                if req_skill_lower == cand_skill_lower:
                    score = 1.0
                elif req_skill_lower in cand_skill_lower or cand_skill_lower in req_skill_lower:
                    score = 0.8
                else:
                    # Use Gemini to calculate semantic similarity if available
                    if self.is_ai_available and self.model:
                        try:
                            response = self.model.generate_content(
                                f"On a scale of 0 to 1, how similar are these skills: '{req_skill}' and '{cand_skill}'? "
                                "Respond with only the number."
                            )
                            try:
                                score = float(response.text.strip())
                            except ValueError:
                                score = 0.4  # Default similarity if parsing fails
                        except Exception:
                            # Fallback to simple token-based similarity
                            req_tokens = set(req_skill_lower.split())
                            cand_tokens = set(cand_skill_lower.split())
                            if req_tokens and cand_tokens:
                                score = len(req_tokens & cand_tokens) / max(len(req_tokens), len(cand_tokens))
                            else:
                                score = 0.3
                    else:
                        # Fallback to simple token-based similarity
                        req_tokens = set(req_skill_lower.split())
                        cand_tokens = set(cand_skill_lower.split())
                        if req_tokens and cand_tokens:
                            score = len(req_tokens & cand_tokens) / max(len(req_tokens), len(cand_tokens))
                        else:
                            score = 0.3
                
                if score > best_score:
                    best_score = score
                    best_match = cand_skill
            
            if best_score >= 0.7:  # Consider it a match if similarity is at least 70%
                matched += best_score
                matches[req_skill] = {
                    'matched_with': best_match,
                    'score': best_score
                }
        
        match_percentage = (matched / total_required) * 100 if total_required > 0 else 0
        
        # Create a more detailed result for the frontend
        skills_details = {
            'matched': [],
            'missing': []
        }
        
        for req_skill in required_skills:
            if req_skill in matches:
                skills_details['matched'].append({
                    'skill': req_skill,
                    'matched_with': matches[req_skill]['matched_with'],
                    'score': matches[req_skill]['score']
                })
            else:
                skills_details['missing'].append(req_skill)
        
        return match_percentage, skills_details
    
    def calculate_experience_match(self, required_years, candidate_experience):
        """Calculate the match percentage for work experience"""
        if not candidate_experience:
            return 0
        
        total_years = sum(exp.get('duration_years', 0) for exp in candidate_experience)
        if total_years >= required_years:
            return 100
        return (total_years / required_years) * 100
    
    def calculate_education_match(self, required_education, candidate_education):
        """Calculate the match percentage for education"""
        education_levels = {
            'high school': 1,
            'associate': 2,
            'bachelor': 3,
            'master': 4,
            'phd': 5
        }
        
        required_level = 0
        candidate_level = 0
        
        # Find the highest education level for both required and candidate
        for level, score in education_levels.items():
            if level in required_education.lower():
                required_level = score
            for edu in candidate_education:
                if level in edu.get('degree', '').lower():
                    candidate_level = max(candidate_level, score)
        
        if candidate_level >= required_level:
            return 100
        return (candidate_level / required_level) * 100
    
    def calculate_github_relevance(self, required_skills, languages, projects, expertise):
        """Calculate the relevance of GitHub profile to job requirements"""
        if not required_skills:
            return 50  # Default moderate relevance
        
        # Calculate language relevance
        language_relevance = 0
        if languages:
            required_lower = [skill.lower() for skill in required_skills]
            language_matches = 0
            
            for lang, _ in languages.items():
                lang_lower = lang.lower()
                for req in required_lower:
                    if lang_lower == req or lang_lower in req or req in lang_lower:
                        language_matches += 1
                        break
            
            language_relevance = (language_matches / len(required_skills)) * 100 if required_skills else 0
        
        # Calculate project relevance
        project_relevance = 0
        if projects:
            project_count = len(projects)
            project_complexity = sum(project.get('complexity', 5) for project in projects) / project_count if project_count > 0 else 0
            
            # Scale complexity to 0-100
            project_relevance = (project_complexity / 10) * 100
        
        # Calculate expertise relevance
        expertise_relevance = 0
        if expertise:
            expertise_lower = [exp.lower() for exp in expertise]
            required_lower = [skill.lower() for skill in required_skills]
            
            expertise_matches = 0
            for exp in expertise_lower:
                for req in required_lower:
                    if exp == req or exp in req or req in exp:
                        expertise_matches += 1
                        break
            
            expertise_relevance = (expertise_matches / len(required_skills)) * 100 if required_skills else 0
        
        # Calculate overall relevance with weights
        weights = {
            'language': 0.5,
            'project': 0.3,
            'expertise': 0.2
        }
        
        overall_relevance = (
            language_relevance * weights['language'] +
            project_relevance * weights['project'] +
            expertise_relevance * weights['expertise']
        )
        
        return overall_relevance
    
    def calculate_linkedin_relevance(self, job_posting, linkedin_data):
        """Calculate the relevance of LinkedIn profile to job requirements"""
        if not linkedin_data:
            return 0
            
        # Extract skills from LinkedIn data
        linkedin_skills = linkedin_data.get('skills', [])
        required_skills = job_posting.required_skills
        
        # Calculate skill overlap
        if not required_skills or not linkedin_skills:
            skill_overlap = 0
        else:
            # Convert to lowercase for better matching
            linkedin_skills_lower = [s.lower() for s in linkedin_skills]
            required_skills_lower = [s.lower() for s in required_skills]
            
            # Count matches (exact and partial)
            matches = 0
            for req in required_skills_lower:
                for skill in linkedin_skills_lower:
                    if req == skill or req in skill or skill in req:
                        matches += 1
                        break
            
            skill_overlap = (matches / len(required_skills)) * 100 if required_skills else 0
        
        # Calculate title relevance
        position = linkedin_data.get('position', '')
        job_title = job_posting.title
        
        title_relevance = 0
        if position and job_title:
            position_lower = position.lower()
            job_title_lower = job_title.lower()
            
            # Check for exact or partial matches
            if position_lower == job_title_lower:
                title_relevance = 100
            elif position_lower in job_title_lower or job_title_lower in position_lower:
                title_relevance = 70
            else:
                # Check for keyword matches
                keywords = ['developer', 'engineer', 'manager', 'designer', 'analyst', 
                           'architect', 'administrator', 'specialist', 'consultant', 'lead']
                
                for keyword in keywords:
                    if keyword in position_lower and keyword in job_title_lower:
                        title_relevance = 50
                        break
        
        # Calculate industry relevance
        company = linkedin_data.get('company', '')
        industry = linkedin_data.get('industry', '')
        job_company = job_posting.company_name
        
        industry_relevance = 0
        if (company and job_company) or industry:
            # Simple industry match for now
            industry_relevance = 50  # Default reasonable value
        
        # Calculate overall relevance (weighted)
        overall_relevance = (
            skill_overlap * 0.6 +
            title_relevance * 0.3 +
            industry_relevance * 0.1
        )
        
        return overall_relevance
    
    def generate_match_explanation(self, job_posting, parsed_resume, skills_score, experience_score, 
                                  education_score, github_relevance, linkedin_relevance):
        """Generate a human-readable explanation for the match score using MCP"""
        # If AI is not available, generate a good fallback explanation
        if not self.is_ai_available or not self.model:
            # Create fallback explanation
            strengths = []
            improvements = []
            
            # Add strength based on highest score
            max_score = max(skills_score, experience_score, education_score)
            if skills_score >= 70:
                strengths.append(f"Strong match on required skills ({skills_score:.1f}%)")
            elif skills_score < 50:
                improvements.append("Acquire more of the required technical skills")
                
            if experience_score >= 70:
                strengths.append(f"Has {experience_score:.1f}% of the required experience")
            elif experience_score < 50:
                improvements.append("Gain more relevant industry experience")
                
            if education_score >= 80:
                strengths.append("Education qualifications exceed requirements")
            elif education_score < 60:
                improvements.append("May need additional educational qualifications")
                
            # Ensure we have at least some strengths and improvements
            if not strengths:
                strengths.append("Has some relevant qualifications for the position")
            if not improvements:
                improvements.append("Continue developing specialized skills for this role")
                
            explanation = f"This candidate meets {skills_score:.1f}% of the required skills, "
            explanation += f"has {experience_score:.1f}% of the required experience, and "
            explanation += f"their education credentials are a {education_score:.1f}% match. "
            
            if max_score >= 75:
                explanation += "Overall, this is a strong match for the position."
            elif max_score >= 60:
                explanation += "This candidate shows good potential for the role."
            else:
                explanation += "There are some gaps between the candidate's profile and job requirements."
            
            return {
                'detailed': explanation,
                'key_strengths': strengths[:3],  # Limit to 3 strengths
                'areas_for_improvement': improvements[:2]  # Limit to 2 improvements
            }
        
        # Use AI to generate explanation if available
        try:
            # Format prompts for Gemini model
            prompt = f"""Generate a clear, detailed explanation for why this candidate is a good match for the job:
            
Job: {job_posting.title} at {job_posting.company_name}
Job Description: {job_posting.description}
Required Skills: {', '.join(job_posting.required_skills)}
Required Experience: {job_posting.required_experience_years} years
Education: {job_posting.education_level}

Candidate Skills Score: {skills_score:.1f}%
Candidate Experience Score: {experience_score:.1f}%
Candidate Education Score: {education_score:.1f}%

In your explanation:
1. Identify 3 specific areas where the candidate's profile aligns well with the job requirements
2. Mention any potential gaps or areas for improvement
3. Provide an overall assessment of fit
4. Keep it professional, constructive, and concise (150 words max)

Response format:
<explanation>The detailed explanation here...</explanation>
<strengths>- Strength 1
- Strength 2
- Strength 3</strengths>
<improvements>- Improvement 1
- Improvement 2</improvements>
"""
            
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Extract parts from the response
            explanation_match = re.search(r"<explanation>(.*?)</explanation>", response_text, re.DOTALL)
            strengths_match = re.search(r"<strengths>(.*?)</strengths>", response_text, re.DOTALL)
            improvements_match = re.search(r"<improvements>(.*?)</improvements>", response_text, re.DOTALL)
            
            explanation = explanation_match.group(1).strip() if explanation_match else ""  
            strengths = strengths_match.group(1).strip().split('\n') if strengths_match else []
            improvements = improvements_match.group(1).strip().split('\n') if improvements_match else []
            
            # Clean up the lists
            strengths = [s.strip('- ').strip() for s in strengths if s.strip()]
            improvements = [i.strip('- ').strip() for i in improvements if i.strip()]
            
            return {
                'detailed': explanation,
                'key_strengths': strengths,
                'areas_for_improvement': improvements
            }
        except Exception as e:
            self.logger.error(f"Error generating AI explanation: {str(e)}")
            # Fall back to simplified explanation
            return self.generate_fallback_explanation(skills_score, experience_score, education_score)
    
    def generate_fallback_explanation(self, skills_score, experience_score, education_score):
        """Generate a fallback explanation if AI fails"""
        strengths = []
        improvements = []
        
        # Add strength based on highest score
        max_score = max(skills_score, experience_score, education_score)
        if skills_score >= 70:
            strengths.append(f"Strong match on required skills ({skills_score:.1f}%)")
        elif skills_score < 50:
            improvements.append("Acquire more of the required technical skills")
            
        if experience_score >= 70:
            strengths.append(f"Has {experience_score:.1f}% of the required experience")
        elif experience_score < 50:
            improvements.append("Gain more relevant industry experience")
            
        if education_score >= 80:
            strengths.append("Education qualifications exceed requirements")
        elif education_score < 60:
            improvements.append("May need additional educational qualifications")
            
        # Ensure we have at least some strengths and improvements
        if not strengths:
            strengths.append("Has some relevant qualifications for the position")
        if not improvements:
            improvements.append("Continue developing specialized skills for this role")
            
        explanation = f"This candidate meets {skills_score:.1f}% of the required skills, "
        explanation += f"has {experience_score:.1f}% of the required experience, and "
        explanation += f"their education credentials are a {education_score:.1f}% match. "
        
        if max_score >= 75:
            explanation += "Overall, this is a strong match for the position."
        elif max_score >= 60:
            explanation += "This candidate shows good potential for the role."
        else:
            explanation += "There are some gaps between the candidate's profile and job requirements."
        
        return {
            'detailed': explanation,
            'key_strengths': strengths[:3],  # Limit to 3 strengths
            'areas_for_improvement': improvements[:2]  # Limit to 2 improvements
        }
    
    def analyze_github_profile(self, github_data):
        """Analyze GitHub profile data using MCP and Gemini"""
        if not github_data:
            return None
        
        try:
            if self.is_ai_available and self.model:
                # Use AI to analyze if available
                prompt = f"""Analyze this GitHub profile data and provide key insights on their skills and expertise:
                {json.dumps(github_data, indent=2)}
                
                Return a JSON structure with:
                - languages: list of programming languages detected
                - activity_level: string (low, medium, high)
                - projects: list of objects with name, description, complexity (1-10)
                - expertise: list of areas of expertise
                - quality_assessment: object with code_quality (1-10), documentation (1-10)
                - activity_score: numeric score (1-100)
                """
                
                response = self.model.generate_content(prompt)
                try:
                    return json.loads(response.text)
                except Exception as e:
                    self.logger.warning(f"Failed to parse AI response for GitHub profile: {str(e)}")
            
            # Fallback to simplified analysis
            languages = github_data.get('languages', {})
            repos = github_data.get('repositories', [])
            
            # Sort languages by frequency
            sorted_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)
            top_languages = [lang for lang, _ in sorted_languages[:5]]
            
            # Extract project details
            projects = []
            for repo in repos[:5]:  # Top 5 repos
                projects.append({
                    'name': repo.get('name', ''),
                    'description': repo.get('description', ''),
                    'complexity': min(len(repo.get('languages', {})), 10)  # Simple complexity measure
                })
            
            # Infer expertise from languages and repositories
            expertise = []
            if any(lang in ['javascript', 'typescript', 'react', 'vue', 'angular'] for lang in top_languages):
                expertise.append('Web Development')
            if any(lang in ['python', 'r', 'jupyter'] for lang in top_languages):
                expertise.append('Data Science')
            if any(lang in ['java', 'kotlin'] for lang in top_languages):
                expertise.append('Android Development')
            if any(lang in ['swift', 'objective-c'] for lang in top_languages):
                expertise.append('iOS Development')
            
            # Calculate activity score
            commit_count = sum(repo.get('commit_count', 0) for repo in repos)
            activity_score = min(commit_count // 10, 100)  # Scale to 0-100
            
            return {
                'languages': top_languages,
                'activity_level': 'high' if activity_score > 70 else 'medium' if activity_score > 30 else 'low',
                'projects': projects,
                'expertise': expertise,
                'quality_assessment': {
                    'code_quality': 7,  # Default without deeper analysis
                    'documentation': 6
                },
                'activity_score': activity_score
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing GitHub profile: {str(e)}")
            return None
    
    def analyze_linkedin_profile(self, linkedin_data):
        """Analyze LinkedIn profile data using MCP"""
        if not linkedin_data:
            return None
        
        try:
            if self.is_ai_available and self.model:
                # Use AI to analyze if available
                prompt = f"""Analyze this LinkedIn profile data and provide key insights:
                {json.dumps(linkedin_data, indent=2)}
                
                Return a JSON structure with:
                - position: current position
                - company: current company
                - experience_level: string (junior, mid, senior, executive)
                - skills: list of skills extracted from profile
                - experience_score: numeric score (1-100)
                """
                
                response = self.model.generate_content(prompt)
                try:
                    return json.loads(response.text)
                except Exception as e:
                    self.logger.warning(f"Failed to parse AI response for LinkedIn profile: {str(e)}")
            
            # Fallback to simplified analysis
            position = linkedin_data.get('headline', '')
            company = ""
            experience = linkedin_data.get('experience', [])
            if experience:
                company = experience[0].get('company', '')
            
            # Extract skills
            skills = linkedin_data.get('skills', [])
            
            # Calculate experience score based on years of experience
            total_experience_years = 0
            for exp in experience:
                if 'duration' in exp and 'years' in exp['duration']:
                    total_experience_years += int(exp['duration']['years'])
            
            # Experience level
            experience_level = 'junior'
            if total_experience_years > 10:
                experience_level = 'executive'
            elif total_experience_years > 5:
                experience_level = 'senior'
            elif total_experience_years > 2:
                experience_level = 'mid'
            
            # Experience score
            experience_score = min(total_experience_years * 10, 100)
            
            return {
                'position': position,
                'company': company,
                'experience_level': experience_level,
                'skills': skills,
                'experience_score': experience_score
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing LinkedIn profile: {str(e)}")
            return None
    
    def calculate_match_score(self, job_posting, parsed_resume):
        """Calculate the overall match score between a job posting and a candidate"""
        if not job_posting or not parsed_resume:
            return {"overall_score": 0, "explanation": "Insufficient data for matching."}
            
        # Calculate individual scores
        skills_score, skills_details = self.calculate_skills_match(
            job_posting.required_skills,
            parsed_resume.skills if parsed_resume and hasattr(parsed_resume, 'skills') else []
        )
        
        experience_score = self.calculate_experience_match(
            job_posting.required_experience_years,
            parsed_resume.experience if parsed_resume and hasattr(parsed_resume, 'experience') else []
        )
        
        education_score = self.calculate_education_match(
            job_posting.education_level,
            parsed_resume.education if parsed_resume and hasattr(parsed_resume, 'education') else []
        )
        
        # Get social profile scores using the enhanced analysis
        github_score = None
        linkedin_score = None
        github_relevance = None
        linkedin_relevance = None
        
        # Use social_analysis data from parsed_resume if available
        if hasattr(parsed_resume, 'social_analysis') and parsed_resume.social_analysis:
            social_analysis = parsed_resume.social_analysis
            
            if 'github_analysis' in social_analysis:
                github_data = self.analyze_github_profile(social_analysis['github_analysis'])
                if github_data:
                    github_score = github_data.get('activity_score')
                    
                    # Calculate github relevance to job posting
                    github_relevance = self.calculate_github_relevance(
                        job_posting.required_skills,
                        github_data.get('languages', {}),
                        github_data.get('projects', []),
                        github_data.get('expertise', [])
                    )
            
            if 'linkedin_analysis' in social_analysis:
                linkedin_data = self.analyze_linkedin_profile(social_analysis['linkedin_analysis'])
                if linkedin_data:
                    linkedin_score = linkedin_data.get('experience_score')
                    
                    # Calculate linkedin relevance to job posting
                    linkedin_relevance = self.calculate_linkedin_relevance(
                        job_posting,
                        linkedin_data
                    )
        
        # Use MCP to get an explainable comparison
        explanation = self.generate_match_explanation(
            job_posting, 
            parsed_resume, 
            skills_score, 
            experience_score, 
            education_score,
            github_relevance,
            linkedin_relevance
        )
        
        # Calculate weighted average
        weights = {
            'skills': 0.35,
            'experience': 0.3,
            'education': 0.2,
            'github': 0.075,
            'linkedin': 0.075
        }
        
        base_score = (
            skills_score * weights['skills'] +
            experience_score * weights['experience'] +
            education_score * weights['education']
        )
        
        # Add social scores if available
        social_weight = 0
        if github_score is not None and github_relevance is not None:
            # Weight github score by its relevance to the job
            effective_github_score = github_score * github_relevance / 100
            base_score += effective_github_score * weights['github']
        else:
            social_weight += weights['github']
        
        if linkedin_score is not None and linkedin_relevance is not None:
            # Weight linkedin score by its relevance to the job
            effective_linkedin_score = linkedin_score * linkedin_relevance / 100
            base_score += effective_linkedin_score * weights['linkedin']
        else:
            social_weight += weights['linkedin']
        
        # Redistribute social weight if social scores are not available
        if social_weight > 0:
            base_score = base_score / (1 - social_weight)
        
        return {
            'overall_score': base_score,
            'skills_match': {
                'score': skills_score,
                'details': skills_details
            },
            'experience_match': experience_score,
            'education_match': education_score,
            'github_score': github_score,
            'github_relevance': github_relevance,
            'linkedin_score': linkedin_score,
            'linkedin_relevance': linkedin_relevance,
            'explanation': explanation
        }
