import pdfplumber
import re
import os
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import spacy

# Download necessary NLTK resources
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    # If model not found, download it
    os.system('python -m spacy download en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')

class ResumeParser:
    """
    Class to parse resume PDFs and extract structured data.
    """
    
    def __init__(self, file_path):
        """
        Initialize with the path to the resume PDF file.
        """
        self.file_path = file_path
        
    def parse(self):
        """
        Parse the resume and extract structured information.
        Returns a dictionary with extracted resume data.
        """
        # Extract text from PDF
        text = self._extract_text()
        
        # Extract information
        resume_data = {
            'skills': self._extract_skills(text),
            'education': self._extract_education(text),
            'experience': self._extract_experience(text),
            'raw_text': text
        }
        
        return resume_data
    
    def _extract_text(self):
        """
        Extract text from the PDF file.
        """
        text = ""
        try:
            with pdfplumber.open(self.file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def _extract_skills(self, text):
        """
        Extract skills from the resume text.
        Uses NLP techniques and a predefined list of common skills.
        """
        # Common technical skills (extend this list as needed)
        common_skills = [
            # Programming languages
            'Python', 'Java', 'JavaScript', 'C++', 'C#', 'Ruby', 'PHP', 'Swift', 'Go', 'Rust',
            'TypeScript', 'Kotlin', 'Scala', 'R', 'MATLAB', 'Perl', 'Bash', 'Shell',
            
            # Web development
            'HTML', 'CSS', 'React', 'Angular', 'Vue', 'Node.js', 'Express', 'Django', 'Flask',
            'Spring', 'ASP.NET', 'Laravel', 'Ruby on Rails', 'jQuery', 'Bootstrap', 'Tailwind',
            
            # Data science & ML
            'Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision', 'Data Analysis',
            'Data Science', 'Statistics', 'Regression', 'Classification', 'Clustering',
            'Neural Networks', 'TensorFlow', 'PyTorch', 'Keras', 'scikit-learn', 'Pandas',
            'NumPy', 'SciPy', 'NLTK', 'spaCy', 'Matplotlib', 'Seaborn', 'Tableau', 'Power BI',
            
            # Cloud & DevOps
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'CI/CD', 'Git', 'GitHub',
            'Terraform', 'Ansible', 'Chef', 'Puppet', 'Prometheus', 'Grafana', 'ELK Stack',
            
            # Databases
            'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Cassandra', 'Oracle',
            'SQLite', 'NoSQL', 'DynamoDB', 'Firebase', 'Elasticsearch',
            
            # Other technical skills
            'REST API', 'GraphQL', 'Microservices', 'Agile', 'Scrum', 'Kanban', 'JIRA',
            'Object-Oriented Programming', 'Functional Programming', 'Serverless',
            'Big Data', 'ETL', 'Hadoop', 'Spark', 'Kafka', 'Linux', 'Unix', 'Windows',
            'Cybersecurity', 'Blockchain', 'IoT',
            
            # Soft skills (fewer of these as they're harder to definitively extract)
            'Leadership', 'Communication', 'Teamwork', 'Problem Solving', 'Critical Thinking',
            'Project Management'
        ]
        
        # Process text with spaCy for NER and additional analysis
        doc = nlp(text)
        
        # Find skills by matching with common skills list (case-insensitive)
        found_skills = []
        for skill in common_skills:
            # Look for whole word matches
            skill_pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(skill_pattern, text, re.IGNORECASE):
                found_skills.append(skill)
        
        # Extract skills from the "Skills" section if present
        skills_section = self._extract_section(text, ['skills', 'technical skills', 'core competencies'])
        if skills_section:
            # Tokenize the skills section
            tokens = word_tokenize(skills_section)
            # Get part-of-speech tags
            pos_tags = nltk.pos_tag(tokens)
            
            # Look for nouns and proper nouns
            for word, tag in pos_tags:
                if tag in ['NN', 'NNP'] and len(word) > 2:  # Nouns that aren't too short
                    if word not in [skill.lower() for skill in found_skills] and word not in stopwords.words('english'):
                        found_skills.append(word.capitalize())
        
        return list(set(found_skills))  # Remove duplicates
    
    def _extract_education(self, text):
        """
        Extract education information from the resume text.
        """
        # Extract the education section
        education_section = self._extract_section(text, ['education', 'academic background', 'academic qualifications'])
        
        if not education_section:
            # If no education section found, try to find education keywords in the text
            edu_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college', 'school', 'diploma']
            edu_sentences = []
            
            for sentence in re.split(r'[.\n]', text):
                if any(keyword in sentence.lower() for keyword in edu_keywords):
                    edu_sentences.append(sentence.strip())
            
            return ' '.join(edu_sentences) if edu_sentences else "Not specified"
        
        return education_section
    
    def _extract_experience(self, text):
        """
        Extract work experience information from the resume text.
        """
        # Extract the experience section
        experience_section = self._extract_section(text, [
            'experience', 'work experience', 'employment history', 
            'professional experience', 'work history'
        ])
        
        if not experience_section:
            # If no experience section found, try to find job titles and companies
            job_titles = ['engineer', 'developer', 'manager', 'director', 'analyst', 
                         'consultant', 'specialist', 'coordinator', 'designer']
            exp_sentences = []
            
            for sentence in re.split(r'[.\n]', text):
                if any(title in sentence.lower() for title in job_titles):
                    exp_sentences.append(sentence.strip())
            
            return ' '.join(exp_sentences) if exp_sentences else "Not specified"
        
        return experience_section
    
    def _extract_section(self, text, section_headers):
        """
        Extract a section from the resume based on section headers.
        """
        text_lower = text.lower()
        
        for header in section_headers:
            # Look for the section header
            pattern = r'(?i)(?:\b' + re.escape(header) + r'\b|^\s*' + re.escape(header) + r'\s*$)'
            match = re.search(pattern, text_lower)
            
            if match:
                # Get the section start
                start_index = match.end()
                
                # Find the next section header
                next_section_match = None
                common_headers = [
                    'education', 'experience', 'skills', 'projects', 'certifications',
                    'awards', 'publications', 'references', 'interests', 'languages',
                    'objective', 'summary', 'contact', 'personal'
                ]
                
                for next_header in common_headers:
                    # Skip if it's the current section
                    if next_header in section_headers:
                        continue
                    
                    next_pattern = r'(?i)(?:\b' + re.escape(next_header) + r'\b|^\s*' + re.escape(next_header) + r'\s*$)'
                    next_match = re.search(next_pattern, text_lower[start_index:])
                    
                    if next_match:
                        if not next_section_match or next_match.start() < next_section_match.start():
                            next_section_match = next_match
                
                # Extract section content
                if next_section_match:
                    end_index = start_index + next_section_match.start()
                    section_content = text[start_index:end_index].strip()
                else:
                    section_content = text[start_index:].strip()
                
                return section_content
        
        return "" 