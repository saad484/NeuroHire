# NeuroHire 🧠

![NeuroHire Logo](https://i.ibb.co/YL1ccmm/neurohire-logo.png)

> **AI-Powered Recruitment Platform for Modern Hiring Teams**

[![Next.js](https://img.shields.io/badge/Next.js-14.0-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![Django](https://img.shields.io/badge/Django-4.2-092E20?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![Google AI](https://img.shields.io/badge/Powered_by-Google_Gemini-4285F4?style=for-the-badge&logo=google)](https://ai.google.dev/)

## 🌟 Overview

NeuroHire is an intelligent recruitment platform that leverages cutting-edge AI technologies to revolutionize the hiring process. Our system automatically analyzes resumes, evaluates candidates against job requirements, and provides rich insights to help recruiters make better hiring decisions faster.

<p align="center">
  <img src="https://i.ibb.co/6RrS5kZ/neurohire-dashboard.png" alt="NeuroHire Dashboard" width="80%">
</p>

## ✨ Key Features

### 📄 Advanced Resume Analysis
- **OCR Technology**: Extract text from PDFs and images
- **AI-Powered Parsing**: Accurately identify skills, experience, and education
- **Data Structuring**: Convert unstructured resume data into standardized formats

### 🔍 Social Profile Integration
- **GitHub Analysis**: Evaluate code quality, project complexity, and technical skills
- **LinkedIn Integration**: Analyze professional experience and skill endorsements
- **Comprehensive View**: Combine resume data with social profiles for holistic assessment

### 🎯 Intelligent Job Matching
- **AI-Driven Matching**: Score candidates based on skills, experience, and education fit
- **Detailed Explanations**: Understand why candidates match or don't match positions
- **Visual Insights**: Clear visuals to show match quality across different dimensions

### 💬 RAG-Powered Candidate Discussions
- **Contextual Conversations**: Discuss candidate profiles with AI that understands the context
- **Insightful Q&A**: Ask complex questions about candidates and receive data-backed answers
- **Decision Support**: Get assistance identifying strengths and potential areas of concern

## 🚀 Technology Stack

### Frontend
- **Next.js & React**: Modern, responsive UI with server components
- **Tailwind CSS**: Beautiful, custom-designed interface
- **TypeScript**: Type-safe code for better development experience
- **ShadcnUI**: High-quality UI components

### Backend
- **Django & Django REST Framework**: Robust API architecture
- **PostgreSQL**: Reliable database storage
- **Redis**: Fast caching and task queue management

### AI & Machine Learning
- **Google Gemini AI**: Advanced text analysis and natural language processing
- **Custom NLP Models**: Specialized models for resume parsing and skill matching
- **Model Context Protocol (MCP)**: Our proprietary system for AI-context management

### DevOps
- **Docker**: Containerized deployment for consistency
- **GitHub Actions**: CI/CD pipeline for automated testing and deployment
- **Azure/AWS**: Cloud hosting with scalability in mind

## 📋 Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn
- PostgreSQL (optional, SQLite works for development)

### Backend Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/neurohire.git
cd neurohire/NEUROHIRE_Backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configuration

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd ../NEUROHIRE

# Install dependencies
npm install
# or
yarn install

# Start the development server
npm run dev
# or
yarn dev
```

## 🛠️ System Architecture

<p align="center">
  <img src="https://i.ibb.co/DpBfgQ7/neurohire-architecture.png" alt="NeuroHire Architecture" width="80%">
</p>

## 📊 Demo

### Candidate Analysis
![Candidate Analysis](https://i.ibb.co/qFJ7Hxm/neurohire-candidate-analysis.png)

### Job Matching
![Job Matching](https://i.ibb.co/NjQPz1G/neurohire-job-matching.png)

## 👨‍💻 Team

NeuroHire was developed by a passionate team of developers for the 2025 AI Innovation Hackathon.

- **Ilyas Farkhane** - Full Stack Developer & ML Engineer
- **[Team Member]** - [Role]
- **[Team Member]** - [Role]
- **[Team Member]** - [Role]

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google for providing access to their Generative AI capabilities
- The open-source community for the amazing tools and libraries
- Our mentors and advisors who provided valuable feedback

---

<p align="center">
  <b>Made with ❤️ for the 2025 AI Innovation Hackathon</b>
</p>
