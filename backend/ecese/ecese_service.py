"""
ECESE Service Module

Main service for Education Content Extraction and Structuring Engine.
Handles file uploads, skeleton extraction, paragraph extraction,
and semantic scope guarding.
"""

import os
import uuid
import shutil
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

from .skeleton_extractor import SkeletonExtractor
from .paragraph_extractor import ParagraphExtractor
from .scope_guard import create_scope_guard, ScopeGuardResult
from .content_structurer import create_content_structurer, StructuredContent
from .ecese_models import ModuleUpload, UploadStatus

logger = logging.getLogger(__name__)


class ECESEService:
    """
    Main ECESE service class.
    
    Handles:
    - File uploads (textbook PDF, teacher guide PDF)
    - Skeleton extraction from teacher guides
    - Storage management
    """
    
    # Base upload directory
    UPLOAD_DIR = Path("uploads/documents")
    
    def __init__(self, upload_dir: Optional[str] = None):
        """
        Initialize the ECESE service.
        
        Args:
            upload_dir: Optional custom upload directory path
        """
        if upload_dir:
            self.upload_dir = Path(upload_dir)
        else:
            self.upload_dir = self.UPLOAD_DIR
        
        # Ensure upload directory exists
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory storage for uploads (replace with DB in production)
        self._uploads: Dict[str, ModuleUpload] = {}
        
        # Extractors
        self.skeleton_extractor = SkeletonExtractor()
        self.paragraph_extractor = ParagraphExtractor()
        
        # Scope guard (lazy loaded)
        self._scope_guard = None
        
        # Content structurer (lazy loaded)
        self._content_structurer = None
    
    def save_uploaded_file(self, file_content: bytes, original_filename: str) -> Tuple[str, str]:
        """
        Save an uploaded file to disk with a unique name.
        
        Args:
            file_content: The file content as bytes
            original_filename: Original filename from upload
            
        Returns:
            Tuple of (unique_filename, full_path)
        """
        # Generate unique filename
        file_ext = Path(original_filename).suffix
        unique_id = str(uuid.uuid4())
        safe_name = "".join(c for c in original_filename if c.isalnum() or c in '._-')
        unique_filename = f"{unique_id}_{safe_name}"
        
        # Full path
        file_path = self.upload_dir / unique_filename
        
        # Write file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return unique_filename, str(file_path)
    
    async def process_upload(
        self,
        module_name: str,
        textbook_content: bytes,
        textbook_filename: str,
        teacher_guide_content: bytes,
        teacher_guide_filename: str
    ) -> ModuleUpload:
        """
        Process a complete module upload.
        
        Args:
            module_name: Name of the module (e.g., "History")
            textbook_content: Textbook PDF content
            textbook_filename: Original textbook filename
            teacher_guide_content: Teacher guide PDF content
            teacher_guide_filename: Original teacher guide filename
            
        Returns:
            ModuleUpload object with upload details
        """
        # Generate upload ID
        upload_id = str(uuid.uuid4())
        
        # Save textbook
        textbook_unique_name, textbook_path = self.save_uploaded_file(
            textbook_content, 
            textbook_filename
        )
        
        # Save teacher guide
        guide_unique_name, guide_path = self.save_uploaded_file(
            teacher_guide_content,
            teacher_guide_filename
        )
        
        # Create upload record
        upload = ModuleUpload(
            id=upload_id,
            module_name=module_name,
            textbook_path=textbook_path,
            teacher_guide_path=guide_path,
            status=UploadStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Store in memory (replace with DB)
        self._uploads[upload_id] = upload
        
        return upload
    
    def extract_skeleton(self, upload_id: str) -> Dict[str, List[str]]:
        """
        Extract skeleton from the teacher guide of an upload.
        
        Args:
            upload_id: The upload ID
            
        Returns:
            Skeleton dictionary
        """
        if upload_id not in self._uploads:
            raise ValueError(f"Upload not found: {upload_id}")
        
        upload = self._uploads[upload_id]
        
        # Update status
        upload.status = UploadStatus.PROCESSING
        upload.updated_at = datetime.utcnow()
        
        try:
            # Extract skeleton from teacher guide
            skeleton = self.skeleton_extractor.extract_skeleton(upload.teacher_guide_path)
            
            # Update upload with skeleton
            upload.skeleton = skeleton
            upload.status = UploadStatus.COMPLETED
            upload.updated_at = datetime.utcnow()
            
            return skeleton
            
        except Exception as e:
            upload.status = UploadStatus.FAILED
            upload.error_message = str(e)
            upload.updated_at = datetime.utcnow()
            raise
    
    def get_upload(self, upload_id: str) -> Optional[ModuleUpload]:
        """
        Get an upload by ID.
        
        Args:
            upload_id: The upload ID
            
        Returns:
            ModuleUpload or None
        """
        return self._uploads.get(upload_id)
    
    def get_all_uploads(self) -> List[ModuleUpload]:
        """
        Get all uploads.
        
        Returns:
            List of all ModuleUpload objects
        """
        return list(self._uploads.values())
    
    def delete_upload(self, upload_id: str) -> bool:
        """
        Delete an upload and its files.
        
        Args:
            upload_id: The upload ID
            
        Returns:
            True if deleted, False if not found
        """
        if upload_id not in self._uploads:
            return False
        
        upload = self._uploads[upload_id]
        
        # Delete files
        try:
            if os.path.exists(upload.textbook_path):
                os.remove(upload.textbook_path)
            if os.path.exists(upload.teacher_guide_path):
                os.remove(upload.teacher_guide_path)
        except Exception:
            pass  # Continue even if file deletion fails
        
        # Remove from storage
        del self._uploads[upload_id]
        
        return True
    
    def get_skeleton_stats(self, skeleton: Dict[str, List[str]]) -> Dict:
        """
        Get statistics about a skeleton.
        
        Args:
            skeleton: The skeleton dictionary
            
        Returns:
            Statistics dictionary
        """
        return self.skeleton_extractor.get_extraction_stats(skeleton)
    
    def extract_paragraphs(self, upload_id: str) -> List[str]:
        """
        Extract paragraphs from the textbook of an upload.
        
        Args:
            upload_id: The upload ID
            
        Returns:
            List of paragraph strings
        """
        if upload_id not in self._uploads:
            raise ValueError(f"Upload not found: {upload_id}")
        
        upload = self._uploads[upload_id]
        
        try:
            # Extract paragraphs from textbook
            paragraphs = self.paragraph_extractor.extract_paragraphs(upload.textbook_path)
            logger.info(f"Extracted {len(paragraphs)} paragraphs from textbook")
            return paragraphs
            
        except Exception as e:
            logger.error(f"Failed to extract paragraphs: {e}")
            raise
    
    def get_paragraph_stats(self, paragraphs: List[str]) -> Dict:
        """
        Get statistics about extracted paragraphs.
        
        Args:
            paragraphs: List of paragraph strings
            
        Returns:
            Statistics dictionary
        """
        return self.paragraph_extractor.get_extraction_stats(paragraphs)
    
    @property
    def scope_guard(self):
        """Lazy-load the semantic scope guard."""
        if self._scope_guard is None:
            self._scope_guard = create_scope_guard(
                use_semantic=True,
                similarity_threshold=0.4,
                log_rejected=True
            )
        return self._scope_guard
    
    @property
    def content_structurer(self):
        """Lazy-load the content structurer."""
        if self._content_structurer is None:
            self._content_structurer = create_content_structurer(
                use_api=True,
                model="llama3-8b-8192"
            )
        return self._content_structurer
    
    def apply_scope_guard(
        self, 
        upload_id: str,
        similarity_threshold: float = 0.4
    ) -> Dict[str, Any]:
        """
        Apply semantic scope guard to match paragraphs to topics.
        
        Args:
            upload_id: The upload ID
            similarity_threshold: Minimum similarity to keep (0-1)
            
        Returns:
            Result dictionary with structured content and statistics
        """
        if upload_id not in self._uploads:
            raise ValueError(f"Upload not found: {upload_id}")
        
        upload = self._uploads[upload_id]
        
        # Ensure skeleton is extracted
        if not upload.skeleton:
            self.extract_skeleton(upload_id)
        
        # Get all topics from skeleton (units + lessons)
        topics = []
        for unit, lessons in upload.skeleton.items():
            topics.append(unit)
            topics.extend(lessons)
        
        # Extract paragraphs from textbook
        paragraphs = self.extract_paragraphs(upload_id)
        
        # Apply scope guard
        logger.info(f"Applying scope guard with threshold {similarity_threshold}")
        result = self.scope_guard.guard_content(topics, paragraphs)
        
        return {
            "structured_content": result.structured_content,
            "in_scope_count": result.in_scope_count,
            "out_of_scope_count": result.out_of_scope_count,
            "topic_coverage": result.topic_coverage,
            "average_similarity": result.average_similarity,
            "rejected_sample": [
                {"paragraph": p[:100] + "...", "best_score": s}
                for p, s in result.rejected_paragraphs[:5]  # First 5 rejected
            ]
        }
    
    def structure_topic_content(
        self,
        topic: str,
        paragraphs: List[str],
        groq_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Structure paragraphs for a single topic using controlled AI.
        
        This is TRANSFORMATION, not generation:
        - Only restructures provided content
        - Does not add new information
        - Returns structured Markdown
        
        Args:
            topic: The topic name
            paragraphs: List of paragraphs to structure
            groq_api_key: Optional Groq API key
            
        Returns:
            Dictionary with structured content
        """
        if groq_api_key:
            from .content_structurer import ContentStructurer
            structurer = ContentStructurer(api_key=groq_api_key)
        else:
            structurer = self.content_structurer
        
        result = structurer.structure_content(topic, paragraphs)
        
        return {
            "topic": result.topic,
            "structured_markdown": result.structured_markdown,
            "word_count_original": result.word_count_original,
            "word_count_structured": result.word_count_structured,
            "model_used": result.model_used,
            "tokens_used": result.tokens_used
        }
    
    def structure_all_topics(
        self,
        upload_id: str,
        groq_api_key: Optional[str] = None,
        similarity_threshold: float = 0.4
    ) -> Dict[str, Any]:
        """
        Structure all topics from an upload using controlled AI.
        
        Pipeline:
        1. Apply scope guard to get filtered content
        2. Structure each topic with AI
        3. Return complete structured document
        
        Args:
            upload_id: The upload ID
            groq_api_key: Groq API key (required)
            similarity_threshold: Scope guard threshold
            
        Returns:
            Dictionary with all structured topics
        """
        if upload_id not in self._uploads:
            raise ValueError(f"Upload not found: {upload_id}")
        
        upload = self._uploads[upload_id]
        
        # Apply scope guard first
        scope_result = self.apply_scope_guard(upload_id, similarity_threshold)
        filtered_content = scope_result["structured_content"]
        
        # Structure each topic
        if groq_api_key:
            from .content_structurer import ContentStructurer
            structurer = ContentStructurer(api_key=groq_api_key)
        else:
            structurer = self.content_structurer
        
        structured_topics = {}
        total_tokens = 0
        
        for topic, paragraphs in filtered_content.items():
            if paragraphs:  # Only structure topics with content
                result = structurer.structure_content(topic, paragraphs)
                structured_topics[topic] = {
                    "markdown": result.structured_markdown,
                    "word_count_original": result.word_count_original,
                    "word_count_structured": result.word_count_structured,
                    "tokens_used": result.tokens_used
                }
                if result.tokens_used:
                    total_tokens += result.tokens_used
        
        # Create full document
        full_document = structurer.create_full_document(
            module_name=upload.module_name,
            structured_contents={t: structurer.structure_content(t, filtered_content[t]) 
                               for t in structured_topics.keys()},
            include_stats=True
        )
        
        return {
            "upload_id": upload_id,
            "module_name": upload.module_name,
            "topics_structured": len(structured_topics),
            "total_tokens_used": total_tokens,
            "structured_topics": structured_topics,
            "full_document": full_document,
            "scope_guard_stats": {
                "in_scope": scope_result["in_scope_count"],
                "out_of_scope": scope_result["out_of_scope_count"],
                "avg_similarity": scope_result["average_similarity"]
            }
        }
    
    def process_complete_module(
        self, 
        upload_id: str,
        similarity_threshold: float = 0.4
    ) -> Dict[str, Any]:
        """
        Complete processing pipeline for a module.
        
        1. Extract skeleton from teacher guide
        2. Extract paragraphs from textbook
        3. Apply scope guard to map content
        
        Args:
            upload_id: The upload ID
            similarity_threshold: Minimum similarity to keep
            
        Returns:
            Complete processing result
        """
        if upload_id not in self._uploads:
            raise ValueError(f"Upload not found: {upload_id}")
        
        upload = self._uploads[upload_id]
        
        try:
            upload.status = UploadStatus.PROCESSING
            upload.updated_at = datetime.utcnow()
            
            # Step 1: Extract skeleton
            skeleton = self.extract_skeleton(upload_id)
            skeleton_stats = self.get_skeleton_stats(skeleton)
            
            # Step 2: Extract paragraphs
            paragraphs = self.extract_paragraphs(upload_id)
            paragraph_stats = self.get_paragraph_stats(paragraphs)
            
            # Step 3: Apply scope guard
            scope_result = self.apply_scope_guard(upload_id, similarity_threshold)
            
            upload.status = UploadStatus.COMPLETED
            upload.updated_at = datetime.utcnow()
            
            return {
                "upload_id": upload_id,
                "module_name": upload.module_name,
                "skeleton": skeleton,
                "skeleton_stats": skeleton_stats,
                "paragraph_stats": paragraph_stats,
                "scope_guard_result": scope_result,
                "status": "completed"
            }
            
        except Exception as e:
            upload.status = UploadStatus.FAILED
            upload.error_message = str(e)
            upload.updated_at = datetime.utcnow()
            raise


# Singleton instance
ecese_service = ECESEService()

