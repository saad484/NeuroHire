"""
Simplified RAG service that works without requiring AI dependencies.
This is a temporary placeholder until the full AI services can be installed.
"""

class SimpleRAGService:
    """A simplified RAG service without AI dependencies"""
    
    def __init__(self):
        self.vector_stores = {}  # Map of candidate_id to "vector store"
    
    def get_vector_store(self, candidate_profile):
        """Get or create vector store for candidate (simplified)"""
        candidate_id = candidate_profile.id
        
        if candidate_id not in self.vector_stores:
            # Create a simple "vector store" with candidate information
            self.vector_stores[candidate_id] = {
                'name': candidate_profile.user.get_full_name() if hasattr(candidate_profile, 'user') else 'Unknown',
                'profile_info': self._extract_profile_info(candidate_profile),
                'skills': candidate_profile.parsed_resume.skills if hasattr(candidate_profile, 'parsed_resume') and candidate_profile.parsed_resume and candidate_profile.parsed_resume.skills else [],
                'experience': candidate_profile.parsed_resume.experience if hasattr(candidate_profile, 'parsed_resume') and candidate_profile.parsed_resume and candidate_profile.parsed_resume.experience else [],
                'education': candidate_profile.parsed_resume.education if hasattr(candidate_profile, 'parsed_resume') and candidate_profile.parsed_resume and candidate_profile.parsed_resume.education else []
            }
            
        return self.vector_stores.get(candidate_id)
    
    def _extract_profile_info(self, candidate_profile):
        """Extract basic profile information"""
        info = {}
        
        if hasattr(candidate_profile, 'user'):
            info['full_name'] = candidate_profile.user.get_full_name()
            info['username'] = candidate_profile.user.username
            info['email'] = candidate_profile.user.email
            
        if hasattr(candidate_profile, 'parsed_resume') and candidate_profile.parsed_resume:
            info['email'] = candidate_profile.parsed_resume.email
            info['phone'] = candidate_profile.parsed_resume.phone
        
        return info
    
    def retrieve_context(self, candidate_profile, query, top_k=5):
        """Retrieve relevant context based on user query (simplified)"""
        vector_store = self.get_vector_store(candidate_profile)
        
        if not vector_store:
            return []
        
        # In the simplified version, just return all the info
        context = []
        
        # Basic info
        context.append(f"Candidate: {vector_store.get('name', 'Unknown')}")
        
        # Skills
        if 'skills' in vector_store and vector_store['skills']:
            context.append(f"Skills: {', '.join(vector_store['skills'])}")
        
        # Experience
        if 'experience' in vector_store and vector_store['experience']:
            for exp in vector_store['experience'][:2]:  # Limit to first 2 experiences
                context.append(f"Experience: {exp.get('title', 'Unknown')} at {exp.get('company', 'Unknown')}")
        
        # Education
        if 'education' in vector_store and vector_store['education']:
            for edu in vector_store['education'][:2]:  # Limit to first 2 educations
                context.append(f"Education: {edu.get('degree', 'Unknown')} at {edu.get('institution', 'Unknown')}")
                
        return context
    
    def generate_response(self, candidate_profile, query, conversation_history=None):
        """Generate response to query about candidate (simplified)"""
        context = self.retrieve_context(candidate_profile, query)
        
        if not context:
            return "I don't have enough information about this candidate to answer your question."
        
        # Generate a simple response based on the query
        if "skills" in query.lower():
            vector_store = self.get_vector_store(candidate_profile)
            skills = vector_store.get('skills', [])
            if skills:
                return f"This candidate has the following skills: {', '.join(skills)}."
            else:
                return "I don't have information about this candidate's skills."
                
        elif "experience" in query.lower():
            vector_store = self.get_vector_store(candidate_profile)
            experience = vector_store.get('experience', [])
            if experience:
                exp_text = []
                for exp in experience:
                    exp_text.append(f"{exp.get('title', 'Unknown')} at {exp.get('company', 'Unknown')}")
                return f"This candidate has experience as: {'; '.join(exp_text)}."
            else:
                return "I don't have information about this candidate's experience."
                
        elif "education" in query.lower():
            vector_store = self.get_vector_store(candidate_profile)
            education = vector_store.get('education', [])
            if education:
                edu_text = []
                for edu in education:
                    edu_text.append(f"{edu.get('degree', 'Unknown')} at {edu.get('institution', 'Unknown')}")
                return f"This candidate's education includes: {'; '.join(edu_text)}."
            else:
                return "I don't have information about this candidate's education."
                
        else:
            # Generic response
            return f"This is a simplified response about the candidate. To get the full AI-powered responses, please install the required AI dependencies. The candidate's basic information includes: {' '.join(context)}"
