from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
import os
import uuid
from django.conf import settings

from resume_parser.parser import ResumeParser
from search_engine.engine import SearchEngine

class ResumeUploadView(APIView):
    """
    API view to handle resume uploads.
    """
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        resume_file = request.FILES.get('resume')
        name = request.data.get('name')
        email = request.data.get('email')
        phone = request.data.get('phone', '')
        
        if not resume_file or not name or not email:
            return Response(
                {'error': 'Resume, name, and email are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create directory if it doesn't exist
        os.makedirs(settings.RESUME_UPLOAD_DIR, exist_ok=True)
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}_{resume_file.name}"
        filepath = os.path.join(settings.RESUME_UPLOAD_DIR, filename)
        
        # Save the file
        with open(filepath, 'wb+') as destination:
            for chunk in resume_file.chunks():
                destination.write(chunk)
        
        try:
            # Parse the resume
            parser = ResumeParser(filepath)
            resume_data = parser.parse()
            
            # Add user-provided data
            resume_data['name'] = name
            resume_data['email'] = email
            resume_data['phone'] = phone
            resume_data['resume_path'] = filepath
            
            # Add to search index
            search_engine = SearchEngine()
            candidate_id = search_engine.index_resume(resume_data)
            
            return Response({
                'message': 'Resume uploaded and processed successfully',
                'candidate_id': candidate_id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # Delete the file if processing fails
            if os.path.exists(filepath):
                os.remove(filepath)
            
            return Response(
                {'error': f'Error processing resume: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SearchCandidatesView(APIView):
    """
    API view to search for candidates matching a job description.
    """
    def post(self, request, *args, **kwargs):
        job_description = request.data.get('job_description')
        
        if not job_description:
            return Response(
                {'error': 'Job description is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Search for matching candidates
            search_engine = SearchEngine()
            candidates = search_engine.search(job_description)
            
            return Response({
                'candidates': candidates
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Error searching candidates: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 