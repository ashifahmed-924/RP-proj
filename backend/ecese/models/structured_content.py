"""
Structured Content Model (Step 6)

MongoDB schema for storing structured educational content.
This is the final output of the ECESE pipeline - curriculum-aligned,
AI-structured content ready for student access.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from bson import ObjectId
from enum import Enum


class ContentStatus(str, Enum):
    """Status of structured content."""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class StructuredContent:
    """
    MongoDB model for structured educational content.
    
    This represents the final, AI-structured learning material
    that has been extracted from textbooks and aligned to curriculum.
    
    Attributes:
        _id: MongoDB ObjectId
        module_name: Name of the module (e.g., "History Grade 10")
        unit_name: Name of the unit (e.g., "Unit 1: Ancient Civilizations")
        topic_name: Name of the topic/lesson (e.g., "Lesson 1.1: Mesopotamia")
        structured_markdown: The AI-structured content in Markdown format
        original_paragraphs: Original paragraphs before structuring
        approved: Whether content has been approved by teacher/admin
        status: Content status (draft, pending_review, approved, published)
        created_by: Teacher ID who created/uploaded the content
        reviewed_by: Teacher/Admin ID who approved the content
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
        approved_at: Timestamp of approval
        metadata: Additional metadata (word counts, tokens used, etc.)
    """
    
    COLLECTION_NAME = 'structured_contents'
    
    def __init__(
        self,
        module_name: str,
        unit_name: str,
        topic_name: str,
        structured_markdown: str,
        created_by: ObjectId,
        original_paragraphs: Optional[List[str]] = None,
        approved: bool = False,
        status: ContentStatus = ContentStatus.DRAFT,
        reviewed_by: Optional[ObjectId] = None,
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        approved_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self._id = _id or ObjectId()
        self.module_name = module_name
        self.unit_name = unit_name
        self.topic_name = topic_name
        self.structured_markdown = structured_markdown
        self.original_paragraphs = original_paragraphs or []
        self.approved = approved
        self.status = status if isinstance(status, ContentStatus) else ContentStatus(status)
        self.created_by = created_by
        self.reviewed_by = reviewed_by
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.approved_at = approved_at
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to MongoDB document."""
        return {
            '_id': self._id,
            'module_name': self.module_name,
            'unit_name': self.unit_name,
            'topic_name': self.topic_name,
            'structured_markdown': self.structured_markdown,
            'original_paragraphs': self.original_paragraphs,
            'approved': self.approved,
            'status': self.status.value,
            'created_by': self.created_by,
            'reviewed_by': self.reviewed_by,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'approved_at': self.approved_at,
            'metadata': self.metadata
        }
    
    def to_response_dict(self) -> Dict[str, Any]:
        """Convert to API response dictionary."""
        return {
            'id': str(self._id),
            'module_name': self.module_name,
            'unit_name': self.unit_name,
            'topic_name': self.topic_name,
            'structured_markdown': self.structured_markdown,
            'original_paragraph_count': len(self.original_paragraphs),
            'approved': self.approved,
            'status': self.status.value,
            'created_by': str(self.created_by),
            'reviewed_by': str(self.reviewed_by) if self.reviewed_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StructuredContent':
        """Create instance from MongoDB document."""
        return cls(
            _id=data.get('_id'),
            module_name=data['module_name'],
            unit_name=data['unit_name'],
            topic_name=data['topic_name'],
            structured_markdown=data['structured_markdown'],
            original_paragraphs=data.get('original_paragraphs', []),
            approved=data.get('approved', False),
            status=data.get('status', ContentStatus.DRAFT),
            created_by=data['created_by'],
            reviewed_by=data.get('reviewed_by'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            approved_at=data.get('approved_at'),
            metadata=data.get('metadata', {})
        )


class ModuleContent:
    """
    MongoDB model for a complete module's content.
    
    Groups all structured content for a module together.
    """
    
    COLLECTION_NAME = 'module_contents'
    
    def __init__(
        self,
        module_name: str,
        created_by: ObjectId,
        upload_id: Optional[str] = None,
        description: Optional[str] = None,
        units: Optional[List[Dict]] = None,
        total_topics: int = 0,
        approved_topics: int = 0,
        status: ContentStatus = ContentStatus.DRAFT,
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self._id = _id or ObjectId()
        self.module_name = module_name
        self.upload_id = upload_id
        self.description = description
        self.units = units or []
        self.total_topics = total_topics
        self.approved_topics = approved_topics
        self.status = status if isinstance(status, ContentStatus) else ContentStatus(status)
        self.created_by = created_by
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to MongoDB document."""
        return {
            '_id': self._id,
            'module_name': self.module_name,
            'upload_id': self.upload_id,
            'description': self.description,
            'units': self.units,
            'total_topics': self.total_topics,
            'approved_topics': self.approved_topics,
            'status': self.status.value,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def to_response_dict(self) -> Dict[str, Any]:
        """Convert to API response dictionary."""
        return {
            'id': str(self._id),
            'module_name': self.module_name,
            'upload_id': self.upload_id,
            'description': self.description,
            'units': self.units,
            'total_topics': self.total_topics,
            'approved_topics': self.approved_topics,
            'completion_percent': (self.approved_topics / self.total_topics * 100) if self.total_topics > 0 else 0,
            'status': self.status.value,
            'created_by': str(self.created_by),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModuleContent':
        """Create instance from MongoDB document."""
        return cls(
            _id=data.get('_id'),
            module_name=data['module_name'],
            upload_id=data.get('upload_id'),
            description=data.get('description'),
            units=data.get('units', []),
            total_topics=data.get('total_topics', 0),
            approved_topics=data.get('approved_topics', 0),
            status=data.get('status', ContentStatus.DRAFT),
            created_by=data['created_by'],
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )


class Enrollment:
    """
    MongoDB model for student module enrollments.
    
    Tracks which students are enrolled in which modules.
    
    Attributes:
        _id: MongoDB ObjectId
        student_id: Student user ID
        module_name: Name of the module
        enrolled_at: Timestamp of enrollment
        updated_at: Last update timestamp
    """
    
    COLLECTION_NAME = 'enrollments'
    
    def __init__(
        self,
        student_id: ObjectId,
        module_name: str,
        _id: Optional[ObjectId] = None,
        enrolled_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self._id = _id or ObjectId()
        self.student_id = student_id
        self.module_name = module_name
        self.enrolled_at = enrolled_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to MongoDB document."""
        return {
            '_id': self._id,
            'student_id': self.student_id,
            'module_name': self.module_name,
            'enrolled_at': self.enrolled_at,
            'updated_at': self.updated_at
        }
    
    def to_response_dict(self) -> Dict[str, Any]:
        """Convert to API response dictionary."""
        return {
            'id': str(self._id),
            'student_id': str(self.student_id),
            'module_name': self.module_name,
            'enrolled_at': self.enrolled_at.isoformat() if self.enrolled_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Enrollment':
        """Create instance from MongoDB document."""
        return cls(
            _id=data.get('_id'),
            student_id=data['student_id'],
            module_name=data['module_name'],
            enrolled_at=data.get('enrolled_at'),
            updated_at=data.get('updated_at')
        )




