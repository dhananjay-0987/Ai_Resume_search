# AI Resume Analyzer

An AI-powered resume analysis system that allows recruiters to search for candidates matching their job descriptions using advanced NLP techniques.

## Features

- **For Recruiters**: Search for candidates by uploading or typing job descriptions
- **For Candidates**: Upload resumes to be matched with relevant job opportunities
- **AI-Powered Matching**: Using Sentence-BERT for embeddings and FAISS for vector similarity search
- **Smart Resume Parsing**: Extract key information from resumes using pdfplumber and NLP tools

## Tech Stack

- **Frontend**: React with TypeScript and Tailwind CSS
- **Backend**: Django with Django REST Framework
- **NLP and Vector Search**:
  - Sentence-BERT for text embeddings
  - FAISS for efficient vector similarity search
  - PDFPlumber for PDF parsing
  - NLTK and SpaCy for NLP processing

## Setup Instructions

### Prerequisites

- Python 3.8+ with pip
- Node.js 14+ with npm
- Git

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run database migrations:
   ```
   python manage.py migrate
   ```

5. Start the Django development server:
   ```
   python manage.py runserver
   ```

The backend server will be running at http://localhost:8000/

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Create a `.env` file with the backend API URL:
   ```
   REACT_APP_API_URL=http://localhost:8000/api
   ```

4. Start the React development server:
   ```
   npm start
   ```

The frontend will be running at http://localhost:3000/

## Usage

### For Recruiters

1. Navigate to the "Recruiter Search" page
2. Enter or paste your job description
3. Click "Find Matching Candidates"
4. View candidates ranked by match score

### For Candidates

1. Navigate to the "Upload Resume" page
2. Fill in your details and upload your resume (PDF format)
3. Submit your information
4. Your profile will be added to the database for recruiters to find

## Development

### Backend Structure

- `resume_analyzer/` - Django project settings
- `api/` - REST API endpoints
- `resume_parser/` - PDF parsing and information extraction
- `search_engine/` - Vector search using FAISS and Sentence-BERT

### Frontend Structure

- `src/components/` - Reusable UI components
- `src/pages/` - Page components for different routes
- `src/services/` - API services for backend communication

## License

This project is licensed under the MIT License - see the LICENSE file for details. "# Ai_Resume_search" 
