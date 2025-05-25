import json
import google.generativeai as genai
from django.conf import settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
import tempfile
import os

class RAGService:
    """
    Retrieval Augmented Generation service for discussing candidate profiles
    """
    
    def __init__(self):
        # Initialize Gemini API
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Initialize embeddings model for text indexing
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Initialize text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        
        # Create temporary directory for vector indices
        self.temp_dir = tempfile.mkdtemp()
        self.vector_stores = {}  # Map of candidate_id to vector store
        
    def _create_index_for_candidate(self, candidate_profile):
        """Create or update a vector index for a candidate profile"""
        if not candidate_profile:
            return None
            
        # Get all available information
        parsed_resume = candidate_profile.parsed_resume
        if not parsed_resume:
            return None
            
        # Combine all text information into documents
        documents = []
        
        # Basic information
        basic_info = f"""
        Candidate Name: {parsed_resume.name or 'N/A'}
        Email: {parsed_resume.email or 'N/A'}
        Phone: {parsed_resume.phone or 'N/A'}
        Current Position: {candidate_profile.current_position or 'N/A'}
        Location: {candidate_profile.location or 'N/A'}
        Bio: {candidate_profile.bio or 'N/A'}
        """
        documents.append(basic_info)
        
        # Skills
        if parsed_resume.skills:
            skills_text = "Skills:\n" + "\n".join([f"- {skill}" for skill in parsed_resume.skills])
            documents.append(skills_text)
        
        # Experience
        if parsed_resume.experience:
            for exp in parsed_resume.experience:
                exp_text = f"""
                Experience:
                Title: {exp.get('title', 'N/A')}
                Company: {exp.get('company', 'N/A')}
                Duration: {exp.get('start_date', 'N/A')} to {exp.get('end_date', 'N/A')}
                Description: {exp.get('description', 'N/A')}
                """
                documents.append(exp_text)
        
        # Education
        if parsed_resume.education:
            for edu in parsed_resume.education:
                edu_text = f"""
                Education:
                Degree: {edu.get('degree', 'N/A')}
                Institution: {edu.get('institution', 'N/A')}
                Duration: {edu.get('start_date', 'N/A')} to {edu.get('end_date', 'N/A')}
                Field of Study: {edu.get('field', 'N/A')}
                """
                documents.append(edu_text)
        
        # Social profiles
        social_profiles = candidate_profile.social_profiles.all()
        for profile in social_profiles:
            profile_text = f"""
            Social Profile:
            Platform: {profile.platform}
            URL: {profile.profile_url}
            """
            
            # Include cached profile data if available
            if profile.profile_data:
                profile_text += f"Profile Data: {json.dumps(profile.profile_data, indent=2)}"
                
            documents.append(profile_text)
        
        # Split documents into chunks
        chunks = []
        for doc in documents:
            chunks.extend(self.text_splitter.split_text(doc))
            
        # Create vector store
        vector_store = FAISS.from_texts(chunks, self.embeddings)
        
        # Save the vector store for this candidate
        candidate_id = candidate_profile.id
        self.vector_stores[candidate_id] = vector_store
        
        return vector_store
        
    def get_vector_store(self, candidate_profile):
        """Get or create vector store for candidate"""
        candidate_id = candidate_profile.id
        
        if candidate_id not in self.vector_stores:
            self._create_index_for_candidate(candidate_profile)
            
        return self.vector_stores.get(candidate_id)
        
    def retrieve_context(self, candidate_profile, query, top_k=5):
        """Retrieve relevant context based on user query"""
        vector_store = self.get_vector_store(candidate_profile)
        
        if not vector_store:
            return []
            
        # Search for relevant chunks
        results = vector_store.similarity_search(query, k=top_k)
        
        # Extract just the content
        context_chunks = [doc.page_content for doc in results]
        
        return context_chunks
        
    def generate_response(self, candidate_profile, query, conversation_history=None):
        """Generate response to query about candidate using RAG"""
        # Retrieve relevant context
        context_chunks = self.retrieve_context(candidate_profile, query)
        
        if not context_chunks:
            return "I don't have enough information about this candidate to answer your question."
            
        # Format context and history
        context_text = "\n\n".join(context_chunks)
        
        history_text = ""
        if conversation_history:
            history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
        
        # Create prompt
        prompt = f"""You are a recruitment assistant analyzing candidate profiles.
        
        Candidate Profile Information:
        {context_text}
        
        Previous Conversation:
        {history_text}
        
        User Question: {query}
        
        Based only on the provided candidate information, answer the user's question.
        If the information is not available in the provided context, say so honestly.
        Do not make up information about the candidate.
        Focus on providing objective insights based on the data.
        """
        
        # Generate response
        response = self.model.generate_content(prompt)
        
        return response.text
