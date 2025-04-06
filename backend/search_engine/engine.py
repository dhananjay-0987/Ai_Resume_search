import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import uuid
from django.conf import settings

class SearchEngine:
    """
    Class to handle resume search using Sentence-BERT embeddings and FAISS vector search.
    """
    
    def __init__(self):
        """
        Initialize the search engine with Sentence-BERT model and FAISS index.
        """
        # Initialize paths
        os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
        
        self.index_path = os.path.join(settings.VECTOR_DB_PATH, 'faiss_index.bin')
        self.data_path = os.path.join(settings.VECTOR_DB_PATH, 'candidate_data.json')
        
        # Initialize Sentence-BERT model
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        # Initialize or load FAISS index and candidate data
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """
        Load existing FAISS index and candidate data or create new ones.
        """
        # Load or create FAISS index
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        else:
            self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product (cosine similarity)
        
        # Load or create candidate data
        if os.path.exists(self.data_path):
            with open(self.data_path, 'r') as f:
                self.candidates = json.load(f)
        else:
            self.candidates = {}
    
    def _save_index(self):
        """
        Save FAISS index and candidate data to disk.
        """
        faiss.write_index(self.index, self.index_path)
        
        with open(self.data_path, 'w') as f:
            json.dump(self.candidates, f)
    
    def _create_embedding(self, text: str) -> np.ndarray:
        """
        Create embedding vector for the given text.
        """
        return self.model.encode(text)
    
    def index_resume(self, resume_data: Dict[str, Any]) -> str:
        """
        Index a resume by creating embeddings and storing in FAISS.
        Returns the candidate ID.
        """
        # Generate a unique ID for the candidate
        candidate_id = str(uuid.uuid4())
        
        # Prepare a consolidated text representation of the resume
        text_to_embed = []
        
        # Add skills
        if resume_data.get('skills'):
            text_to_embed.append("Skills: " + ", ".join(resume_data['skills']))
        
        # Add education
        if resume_data.get('education'):
            text_to_embed.append("Education: " + resume_data['education'])
        
        # Add experience
        if resume_data.get('experience'):
            text_to_embed.append("Experience: " + resume_data['experience'])
        
        # Create a single text for embedding
        consolidated_text = " ".join(text_to_embed)
        
        # Add raw text as a fallback
        if not consolidated_text and resume_data.get('raw_text'):
            consolidated_text = resume_data['raw_text']
        
        # Create embedding
        embedding = self._create_embedding(consolidated_text)
        
        # Add to FAISS index
        self.index.add(np.array([embedding], dtype=np.float32))
        
        # Store candidate data
        self.candidates[candidate_id] = {
            'id': candidate_id,
            'name': resume_data.get('name', ''),
            'email': resume_data.get('email', ''),
            'phone': resume_data.get('phone', ''),
            'skills': resume_data.get('skills', []),
            'education': resume_data.get('education', ''),
            'experience': resume_data.get('experience', ''),
            'resume_path': resume_data.get('resume_path', ''),
            'index_position': self.index.ntotal - 1  # Position in the FAISS index
        }
        
        # Save the index and data
        self._save_index()
        
        return candidate_id
    
    def search(self, job_description: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for candidates matching the job description.
        Returns a list of candidate data with match scores.
        """
        if self.index.ntotal == 0:
            return []  # No candidates indexed yet
        
        # Create embedding for the job description
        query_embedding = self._create_embedding(job_description)
        
        # Search in FAISS index
        k = min(top_k, self.index.ntotal)  # Ensure k isn't larger than the number of indexed items
        scores, indices = self.index.search(np.array([query_embedding], dtype=np.float32), k)
        
        # Get candidate data for the search results
        results = []
        for i, idx in enumerate(indices[0]):
            # Find the candidate with this index position
            candidate = None
            for cand_id, cand_data in self.candidates.items():
                if cand_data['index_position'] == idx:
                    candidate = cand_data.copy()
                    break
            
            if candidate:
                # Add the match score (normalize to 0-1 range)
                score = float(scores[0][i])
                normalized_score = (score + 1) / 2  # Convert from [-1,1] to [0,1]
                candidate['match_score'] = normalized_score
                
                # Remove internal data
                if 'index_position' in candidate:
                    del candidate['index_position']
                if 'resume_path' in candidate:
                    del candidate['resume_path']
                
                results.append(candidate)
        
        return results 