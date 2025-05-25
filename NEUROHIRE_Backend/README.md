# NeuroHire Backend

This is the backend API for NeuroHire, an AI-powered recruitment system that uses Computer Vision, OCR, and LLMs to analyze resumes and match candidates to job postings.

## Key Features

1. **Resume Parsing with OCR**
   - Extracts text from various resume formats (PDF, DOCX, images)
   - Uses pre-trained models to identify key sections (competence, experience, formation)
   - Automatically extracts contact information, skills, education, and work experience

2. **Social Profile Analysis (Model Context Protocol)**
   - Extracts GitHub and LinkedIn profiles from resumes
   - Analyzes GitHub repositories for programming languages, project quality, and contribution activity
   - Examines LinkedIn profiles for job history, skills, and professional connections
   - Provides deep insights into candidate qualifications beyond what's in the resume

3. **AI-Powered Job Matching**
   - Compares candidate skills and experience with job requirements
   - Uses the Model Context Protocol (MCP) to evaluate actual projects and work rather than just stated skills
   - Provides detailed match explanations and scoring breakdowns
   - Ranks candidates by match percentage

4. **RAG-Based Candidate Discussion**
   - Chat with an AI about specific candidates
   - Retrieve relevant information based on queries
   - Get intelligent insights based on all available candidate data

## Setup and Installation

1. **Environment Setup**
   ```bash
   # Activate virtual environment
   .\venv\Scripts\activate.ps1
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Database Configuration**
   - Configure PostgreSQL in the `.env` file
   - Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

## API Endpoints

### Resume Management
- `GET /api/resumes/` - List all resumes
- `POST /api/resumes/` - Upload a new resume
- `POST /api/resumes/{id}/parse/` - Parse a resume to extract information
- `GET /api/parsed-resumes/` - List all parsed resumes with extracted information

### Job Posting Management
- `GET /api/jobs/` - List all job postings
- `POST /api/jobs/` - Create a new job posting
- `POST /api/jobs/{id}/match_candidates/` - Match all candidates to this job using MCP
- `GET /api/jobs/{id}/matches/` - Get all candidate matches for a job

### Candidate Profile Management
- `GET /api/candidates/` - List all candidate profiles
- `GET /api/candidates/{id}/social_profiles/` - Get all social profiles for a candidate
- `POST /api/candidates/{id}/analyze_social_profiles/` - Analyze candidate's social profiles using MCP
- `POST /api/candidates/{id}/chat/` - Chat with the RAG system about a candidate

### Candidate Matching
- `GET /api/matches/` - List all candidate matches
- `GET /api/matches/{id}/detailed_analysis/` - Get detailed MCP analysis for a match

## Model Context Protocol (MCP)

The Model Context Protocol is a key feature of NeuroHire that enhances job matching by:

1. **Analyzing Actual Projects**: Rather than relying solely on stated skills, MCP examines GitHub repositories to verify coding skills, project complexity, and technical expertise.

2. **Verifying Professional Experience**: MCP analyzes LinkedIn profiles to validate work history, roles, and industry experience.

3. **Cross-Referencing Information**: MCP creates a confidence score for each skill by verifying it across multiple sources (resume, GitHub, LinkedIn).

4. **Project-Job Relevance**: MCP specifically evaluates how relevant a candidate's projects are to the requirements of a specific job.

5. **Explainable Matching**: MCP provides detailed explanations for why a candidate does or doesn't match a job position.

## Running the Server

```bash
python manage.py runserver
```

Access the API at http://localhost:8000/api/

## Example Workflow

1. Upload resumes to the system
2. Parse resumes to extract information
3. Create job postings with required skills and experience
4. Run the matching process to score candidates
5. View detailed match analyses for each candidate
6. Chat with the AI about specific candidates to get insights
