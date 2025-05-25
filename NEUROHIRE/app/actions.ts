// Client-side helper for API endpoints
const API_BASE_URL = "http://localhost:8000";

// This file contains client-side API helper functions
// These are not server actions and should be imported from client components only

export const API_ENDPOINTS = {
  // Authentication
  TOKEN_AUTH: `${API_BASE_URL}/api-token-auth/`,
  
  // Resume parsing
  UPLOAD_RESUME: `${API_BASE_URL}/api/upload-resume/`,
  RESUMES: `${API_BASE_URL}/api/resumes/`,
  PARSED_RESUMES: `${API_BASE_URL}/api/parsed-resumes/`,
  
  // Job matching
  JOBS: `${API_BASE_URL}/api/jobs/`,
  MATCHES: `${API_BASE_URL}/api/matches/`,
  
  // Candidates
  CANDIDATES: `${API_BASE_URL}/api/candidates/`,
  SOCIAL_PROFILES: `${API_BASE_URL}/api/social-profiles/`,
};

