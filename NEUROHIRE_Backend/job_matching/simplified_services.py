"""
Simplified job matching service that works without requiring all AI dependencies.
This is a temporary placeholder until the full AI services can be installed.
"""

class SimpleJobMatcher:
    """An enhanced job matcher that provides realistic matching without requiring all AI dependencies"""
    
    def __init__(self):
        # Tech skill categories for better matching
        self.skill_categories = {
            'frontend': [
                'react', 'vue', 'angular', 'javascript', 'typescript', 'html', 'css', 'sass',
                'bootstrap', 'tailwind', 'material-ui', 'responsive', 'webpack', 'nextjs', 'vuejs'
            ],
            'backend': [
                'python', 'django', 'flask', 'node', 'express', 'fastapi', 'java', 'spring',
                'php', 'laravel', 'ruby', 'rails', 'go', 'rust', 'c#', '.net', 'core'
            ],
            'database': [
                'sql', 'mysql', 'postgresql', 'mongodb', 'nosql', 'redis', 'elasticsearch',
                'firebase', 'orm', 'database', 'dynamodb', 'cassandra'
            ],
            'devops': [
                'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'ci/cd', 'jenkins', 'terraform',
                'ansible', 'github actions', 'cloud', 'deployment'
            ],
            'mobile': [
                'android', 'ios', 'swift', 'kotlin', 'react native', 'flutter', 'mobile',
                'pwa', 'responsive'
            ],
            'ai_ml': [
                'machine learning', 'artificial intelligence', 'tensorflow', 'pytorch', 'keras',
                'nlp', 'computer vision', 'neural network', 'deep learning', 'data science'
            ],
            'data': [
                'data analysis', 'big data', 'tableau', 'power bi', 'etl', 'pandas',
                'hadoop', 'spark', 'data visualization', 'data pipeline'
            ],
            'security': [
                'security', 'penetration testing', 'authentication', 'encryption',
                'oauth', 'jwt', 'cybersecurity', 'hacking', 'firewall'
            ],
            'blockchain': [
                'blockchain', 'ethereum', 'solidity', 'smart contracts', 'web3', 'cryptocurrency',
                'nft', 'defi'
            ]
        }
        
        # Common tools and technologies associated with programming languages
        self.language_ecosystems = {
            'python': ['django', 'flask', 'fastapi', 'tensorflow', 'pytorch', 'pandas', 'numpy'],
            'javascript': ['react', 'vue', 'angular', 'node', 'express', 'webpack', 'npm'],
            'typescript': ['angular', 'react', 'nextjs', 'node', 'express'],
            'java': ['spring', 'hibernate', 'maven', 'gradle'],
            'c#': ['.net', 'asp.net', 'entity framework', 'xamarin'],
            'php': ['laravel', 'symfony', 'wordpress'],
            'ruby': ['rails', 'sinatra'],
            'go': ['gin', 'echo', 'gorilla'],
            'swift': ['ios', 'cocoa', 'xcode'],
            'kotlin': ['android', 'spring boot']
        }
    
    def calculate_skills_match(self, required_skills, candidate_skills):
        """Calculate the match percentage between required and candidate skills"""
        if not required_skills or not candidate_skills:
            return 0, {
                'percentage': 0,
                'matched': [],
                'missing': list(required_skills) if required_skills else []
            }
        
        # Normalize all skills to lowercase
        required_lower = [skill.lower() for skill in required_skills]
        candidate_lower = [skill.lower() for skill in candidate_skills]
        
        # Direct matches (exact matches)
        direct_matches = set(required_lower) & set(candidate_lower)
        
        # Partial matches (substring matches)
        partial_matches = {}
        for req_skill in required_lower:
            if req_skill in direct_matches:
                continue
                
            for cand_skill in candidate_lower:
                if req_skill in cand_skill or cand_skill in req_skill:
                    # Calculate similarity score based on length ratio
                    similarity = min(len(req_skill), len(cand_skill)) / max(len(req_skill), len(cand_skill))
                    if similarity >= 0.6:  # Only consider it a partial match if similar enough
                        if req_skill not in partial_matches or similarity > partial_matches[req_skill]['score']:
                            partial_matches[req_skill] = {
                                'matched_with': cand_skill,
                                'score': similarity,
                                'original_form': next(s for s in required_skills if s.lower() == req_skill)
                            }
        
        # Category matches (skills in the same category)
        category_matches = {}
        for req_skill in required_lower:
            if req_skill in direct_matches or req_skill in partial_matches:
                continue
                
            # Find which category the required skill belongs to
            req_skill_category = None
            for category, skills in self.skill_categories.items():
                if any(tech in req_skill for tech in skills):
                    req_skill_category = category
                    break
            
            if req_skill_category:
                # Find candidate skills in the same category
                for cand_skill in candidate_lower:
                    if any(tech in cand_skill for tech in self.skill_categories[req_skill_category]):
                        category_matches[req_skill] = {
                            'matched_with': cand_skill,
                            'score': 0.5,  # Lower score for category matches
                            'category': req_skill_category,
                            'original_form': next(s for s in required_skills if s.lower() == req_skill)
                        }
                        break
        
        # Ecosystem matches (skills in the same language ecosystem)
        ecosystem_matches = {}
        for req_skill in required_lower:
            if req_skill in direct_matches or req_skill in partial_matches or req_skill in category_matches:
                continue
                
            # Check if this is a programming language with an ecosystem
            for language, ecosystem in self.language_ecosystems.items():
                if language in req_skill:
                    # Check if candidate has skills in this ecosystem
                    eco_skills = [s for s in candidate_lower if any(e in s for e in ecosystem)]
                    if eco_skills:
                        ecosystem_matches[req_skill] = {
                            'matched_with': eco_skills[0],  # Use the first match
                            'score': 0.4,  # Even lower score for ecosystem matches
                            'ecosystem': language,
                            'original_form': next(s for s in required_skills if s.lower() == req_skill)
                        }
                        break
        
        # Calculate overall match percentage
        total_required = len(required_skills)
        direct_score = len(direct_matches) * 1.0  # Full weight for direct matches
        partial_score = sum(match['score'] for match in partial_matches.values())
        category_score = sum(match['score'] for match in category_matches.values())
        ecosystem_score = sum(match['score'] for match in ecosystem_matches.values())
        
        total_match_score = direct_score + partial_score + category_score + ecosystem_score
        match_percentage = (total_match_score / total_required) * 100 if total_required > 0 else 0
        
        # Format the result
        all_matches = {}
        
        # Add direct matches
        for skill in direct_matches:
            original_form = next(s for s in required_skills if s.lower() == skill)
            original_candidate = next(s for s in candidate_skills if s.lower() == skill)
            all_matches[original_form] = {
                'matched_with': original_candidate,
                'score': 1.0,
                'match_type': 'direct'
            }
        
        # Add partial matches with original forms
        for req, match in partial_matches.items():
            all_matches[match['original_form']] = {
                'matched_with': next(s for s in candidate_skills if s.lower() == match['matched_with']),
                'score': match['score'],
                'match_type': 'partial'
            }
        
        # Add category matches with original forms
        for req, match in category_matches.items():
            all_matches[match['original_form']] = {
                'matched_with': next(s for s in candidate_skills if s.lower() == match['matched_with']),
                'score': match['score'],
                'match_type': 'category',
                'category': match['category']
            }
        
        # Add ecosystem matches with original forms
        for req, match in ecosystem_matches.items():
            all_matches[match['original_form']] = {
                'matched_with': next(s for s in candidate_skills if s.lower() == match['matched_with']),
                'score': match['score'],
                'match_type': 'ecosystem',
                'ecosystem': match['ecosystem']
            }
        
        # Generate the matched and missing skills lists
        matched_skills = list(all_matches.keys())
        missing_skills = [skill for skill in required_skills if skill not in matched_skills]
        
        # Create a frontend-friendly structure
        result = {
            'percentage': match_percentage,
            'matched': matched_skills,
            'missing': missing_skills,
            'details': all_matches
        }
        
        return match_percentage, result
    
    def calculate_experience_match(self, required_years, candidate_experience):
        """Calculate the match percentage for work experience"""
        if not candidate_experience:
            return 0
        
        # Try to extract actual years from the experience data
        total_years = 0
        
        for exp in candidate_experience:
            # Try to extract duration directly if it exists
            if 'duration_years' in exp:
                total_years += float(exp['duration_years'])
                continue
                
            # Try to calculate from start and end dates
            start_date = exp.get('start_date', '')
            end_date = exp.get('end_date', '')
            
            # Handle 'present' or empty end date
            if not end_date or end_date.lower() in ['present', 'current', 'now']:
                # Assume current year if end date is 'present'
                import datetime
                end_year = datetime.datetime.now().year
            else:
                # Try to extract year from end_date string
                try:
                    # Handle different date formats
                    if '-' in end_date:
                        end_year = int(end_date.split('-')[0])
                    else:
                        end_year = int(end_date)
                except (ValueError, IndexError):
                    # Default to assuming 1 year if we can't parse the dates
                    total_years += 1
                    continue
            
            # Extract start year
            try:
                if start_date:
                    if '-' in start_date:
                        start_year = int(start_date.split('-')[0])
                    else:
                        start_year = int(start_date)
                    duration = end_year - start_year
                    total_years += max(0, duration)  # Ensure non-negative
                else:
                    # If no start date, assume 1 year
                    total_years += 1
            except (ValueError, IndexError):
                # Default to 1 year if we can't parse
                total_years += 1
        
        # If we couldn't extract any meaningful years, use a fallback method
        if total_years == 0 and candidate_experience:
            # Assume 1-2 years per experience entry as a fallback
            total_years = len(candidate_experience) * 1.5
        
        # Calculate match percentage
        if total_years >= required_years:
            return 100
        return (total_years / required_years) * 100 if required_years > 0 else 0
    
    def calculate_education_match(self, required_education, candidate_education):
        """Calculate the match percentage for education"""
        if not candidate_education:
            return 0
            
        # Enhanced education matching with more granular levels and degree fields
        education_levels = {
            'high school': 1,
            'diploma': 1.5,
            'certificate': 1.8,
            'associate': 2,
            'bachelor': 3,
            'undergraduate': 3,
            'bs': 3,
            'ba': 3,
            'master': 4,
            'ms': 4,
            'ma': 4,
            'mba': 4.2,
            'phd': 5,
            'doctorate': 5,
            'post-doctoral': 5.5
        }
        
        # Field relevance factors (bonus multiplier when field matches)
        field_multiplier = 1.2
        
        # Extract key terms from required education
        required_level = 1  # Default to high school
        required_fields = set()
        
        # Extract education level and field from required education
        required_education_lower = required_education.lower()
        for level, score in education_levels.items():
            if level in required_education_lower:
                required_level = max(required_level, score)
                
        # Extract potential field requirements
        common_fields = [
            'computer science', 'engineering', 'business', 'finance', 'marketing',
            'data science', 'mathematics', 'statistics', 'economics', 'accounting',
            'design', 'psychology', 'biology', 'chemistry', 'physics', 'law',
            'healthcare', 'nursing', 'medicine', 'education', 'art'
        ]
        
        for field in common_fields:
            if field in required_education_lower:
                required_fields.add(field)
        
        # Find highest candidate education level
        candidate_level = 0
        field_match_found = False
        
        for edu in candidate_education:
            # Extract degree level
            current_level = 0
            degree_text = edu.get('degree', '').lower()
            
            for level, score in education_levels.items():
                if level in degree_text:
                    current_level = max(current_level, score)
            
            # Extract institution for prestige bonus
            institution = edu.get('institution', '').lower()
            prestige_bonus = 0
            
            # Give slight bonus to prestigious institutions
            prestigious_terms = ['university', 'college', 'institute', 'school']
            if any(term in institution for term in prestigious_terms):
                prestige_bonus = 0.2
            
            # Check for field match
            current_field_match = False
            if required_fields:
                for field in required_fields:
                    if field in degree_text or field in institution:
                        current_field_match = True
                        field_match_found = True
                        break
            
            # Update candidate's best level with any applicable bonuses
            effective_level = current_level + prestige_bonus
            candidate_level = max(candidate_level, effective_level)
        
        # Calculate base match
        base_match = (candidate_level / required_level) * 100 if required_level > 0 else 0
        
        # Apply field relevance bonus if fields match and there were required fields
        final_match = min(100, base_match * (field_multiplier if field_match_found and required_fields else 1.0))
        
        return final_match
    
    def generate_match_explanation(self, job_posting, parsed_resume, skills_score, 
                                  experience_score, education_score, skills_details):
        """Generate a detailed explanation for the match"""
        # Get key matches and misses
        matched_skills = skills_details.get('matched', [])
        missing_skills = skills_details.get('missing', [])
        
        # Format skills nicely
        matched_str = ', '.join(matched_skills[:5])
        if len(matched_skills) > 5:
            matched_str += f" and {len(matched_skills) - 5} more"
            
        missing_str = ', '.join(missing_skills[:3])
        if len(missing_skills) > 3:
            missing_str += f" and {len(missing_skills) - 3} more"
        
        # Generate personalized explanations
        if skills_score >= 80 and experience_score >= 70 and education_score >= 70:
            tier = "excellent"
            explanation = f"This candidate is an excellent match for the {job_posting.title} position. "  \
                         f"They have {matched_str} among their skills, " \
                         f"which covers most of the key requirements. "
        elif skills_score >= 60 and experience_score >= 50 and education_score >= 50:
            tier = "good"
            explanation = f"This candidate is a good match for the {job_posting.title} position. " \
                         f"Their skills include {matched_str}, " \
                         f"though they are missing {missing_str}. "
        elif skills_score >= 40:
            tier = "potential"
            explanation = f"This candidate shows potential for the {job_posting.title} position. " \
                         f"They match on {matched_str}, but lack several key skills. "
        else:
            tier = "weak"
            explanation = f"This candidate is not a strong match for the {job_posting.title} position. " \
                         f"They are missing most of the required skills including {missing_str}. "
        
        # Add experience assessment
        if experience_score >= 100:
            explanation += f"They exceed the required {job_posting.required_experience_years} years of experience. "
        elif experience_score >= 75:
            explanation += f"They have most of the required {job_posting.required_experience_years} years of experience. "
        elif experience_score >= 50:
            explanation += f"They have some relevant experience but less than the required {job_posting.required_experience_years} years. "
        else:
            explanation += f"They have significantly less experience than the required {job_posting.required_experience_years} years. "
        
        # Add education assessment
        if education_score >= 100:
            explanation += f"Their education meets or exceeds the {job_posting.education_level} requirement."
        elif education_score >= 75:
            explanation += f"Their education nearly meets the {job_posting.education_level} requirement."
        else:
            explanation += f"Their education is below the {job_posting.education_level} requirement."
        
        return {
            'summary': f"Candidate matches {skills_score:.1f}% of skills, {experience_score:.1f}% of experience, and {education_score:.1f}% of education requirements.",
            'detailed': explanation,
            'tier': tier
        }
    
    def calculate_match_score(self, job_posting, parsed_resume):
        """Calculate the overall match score between a job posting and a candidate"""
        # Calculate individual scores
        skills_score, skills_details = self.calculate_skills_match(
            job_posting.required_skills,
            parsed_resume.skills if parsed_resume.skills else []
        )
        
        experience_score = self.calculate_experience_match(
            job_posting.required_experience_years,
            parsed_resume.experience if parsed_resume.experience else []
        )
        
        education_score = self.calculate_education_match(
            job_posting.education_level,
            parsed_resume.education if parsed_resume.education else []
        )
        
        # Calculate job-title relevance
        job_title_relevance = 0
        if parsed_resume.experience and job_posting.title:
            job_title_lower = job_posting.title.lower()
            for exp in parsed_resume.experience:
                if 'title' in exp and exp['title']:
                    exp_title_lower = exp['title'].lower()
                    
                    # Direct title match
                    if job_title_lower == exp_title_lower:
                        job_title_relevance = 100
                        break
                    
                    # Partial title match
                    if job_title_lower in exp_title_lower or exp_title_lower in job_title_lower:
                        job_title_relevance = 80
                        break
                    
                    # Keyword matches in title
                    keywords = ['developer', 'engineer', 'manager', 'designer', 'analyst', 'architect',
                               'administrator', 'specialist', 'consultant', 'lead']
                    for keyword in keywords:
                        if keyword in job_title_lower and keyword in exp_title_lower:
                            job_title_relevance = 60
                            break
        
        # Generate explanation
        explanation = self.generate_match_explanation(
            job_posting, 
            parsed_resume, 
            skills_score, 
            experience_score, 
            education_score,
            skills_details
        )
        
        # Calculate weighted average
        weights = {
            'skills': 0.45,         # Skills are the most important factor
            'experience': 0.25,      # Experience is also very important
            'education': 0.15,       # Education is somewhat important
            'job_title_relevance': 0.15  # Previous job titles can indicate fit
        }
        
        # Add variance for more realistic scores
        import random
        variance_factor = random.uniform(0.95, 1.05)  # +/- 5% random variance
        
        overall_score = (
            skills_score * weights['skills'] +
            experience_score * weights['experience'] +
            education_score * weights['education'] +
            job_title_relevance * weights['job_title_relevance']
        ) * variance_factor
        
        # Ensure score is within 0-100 range
        overall_score = max(0, min(100, overall_score))
        
        # Create a structured match results object for the frontend
        return {
            'overall_score': overall_score,
            'skills_match': {
                'percentage': skills_score,  # For backwards compatibility
                'score': skills_score,
                'matched': skills_details.get('matched', []),
                'missing': skills_details.get('missing', [])
            },
            'experience_match': experience_score,
            'education_match': education_score,
            'job_title_relevance': job_title_relevance,
            'explanation': explanation
        }
