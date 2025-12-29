"""
Content Storage Module (Step 6)

Functions to persist structured educational content to MongoDB.
Provides CRUD operations for StructuredContent and ModuleContent.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from bson import ObjectId
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError

from .models.structured_content import (
    StructuredContent, 
    ModuleContent, 
    ContentStatus,
    Enrollment
)

logger = logging.getLogger(__name__)


class ContentStorageError(Exception):
    """Exception for content storage errors."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ContentStorage:
    """
    Storage service for structured educational content.
    
    Handles persistence of ECESE-processed content to MongoDB.
    Integrates with the existing database setup.
    """
    
    def __init__(self, db=None):
        """
        Initialize content storage.
        
        Args:
            db: MongoDB database instance (optional, will use app's DB if not provided)
        """
        self._db = db
        self._initialized = False
    
    @property
    def db(self):
        """Get database instance."""
        if self._db is None:
            # Import here to avoid circular imports
            try:
                import sys
                sys.path.insert(0, '..')
                from database import get_database
                self._db = get_database()
            except ImportError:
                logger.warning("Could not import database module")
                return None
        return self._db
    
    def _ensure_indexes(self):
        """Create necessary indexes for efficient queries."""
        if self._initialized or self.db is None:
            return
        
        try:
            # Indexes for structured_contents collection
            self.db.structured_contents.create_index([
                ('module_name', ASCENDING),
                ('unit_name', ASCENDING),
                ('topic_name', ASCENDING)
            ])
            self.db.structured_contents.create_index('created_by')
            self.db.structured_contents.create_index('status')
            self.db.structured_contents.create_index('approved')
            
            # Indexes for module_contents collection
            self.db.module_contents.create_index('module_name', unique=True)
            self.db.module_contents.create_index('created_by')
            self.db.module_contents.create_index('status')
            
            # Indexes for enrollments collection
            self.db.enrollments.create_index([('student_id', ASCENDING), ('module_name', ASCENDING)], unique=True)
            self.db.enrollments.create_index('student_id')
            self.db.enrollments.create_index('module_name')
            
            self._initialized = True
            logger.info("Content storage indexes created")
        except Exception as e:
            logger.warning(f"Could not create indexes: {e}")
    
    # ==================== Structured Content CRUD ====================
    
    def insert_structured_content(
        self,
        module_name: str,
        unit_name: str,
        topic_name: str,
        structured_markdown: str,
        created_by: str,
        original_paragraphs: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> StructuredContent:
        """
        Insert structured content into MongoDB.
        
        Args:
            module_name: Name of the module
            unit_name: Name of the unit
            topic_name: Name of the topic/lesson
            structured_markdown: The AI-structured content in Markdown
            created_by: Teacher ID who created the content
            original_paragraphs: Original paragraphs before structuring
            metadata: Additional metadata
            
        Returns:
            The created StructuredContent object
        """
        if self.db is None:
            raise ContentStorageError("Database not connected", 500)
        
        self._ensure_indexes()
        
        # Create content object
        content = StructuredContent(
            module_name=module_name,
            unit_name=unit_name,
            topic_name=topic_name,
            structured_markdown=structured_markdown,
            created_by=ObjectId(created_by),
            original_paragraphs=original_paragraphs or [],
            approved=False,
            status=ContentStatus.DRAFT,
            metadata=metadata or {}
        )
        
        # Insert into database
        try:
            result = self.db.structured_contents.insert_one(content.to_dict())
            logger.info(f"Inserted content for topic: {topic_name}")
            return content
        except Exception as e:
            logger.error(f"Failed to insert content: {e}")
            raise ContentStorageError(f"Failed to insert content: {str(e)}", 500)
    
    def insert_multiple_contents(
        self,
        contents: List[Dict[str, Any]],
        created_by: str
    ) -> List[StructuredContent]:
        """
        Insert multiple structured contents at once.
        
        Args:
            contents: List of content dictionaries with module_name, unit_name, 
                     topic_name, structured_markdown, original_paragraphs
            created_by: Teacher ID
            
        Returns:
            List of created StructuredContent objects
        """
        if self.db is None:
            raise ContentStorageError("Database not connected", 500)
        
        self._ensure_indexes()
        
        created_contents = []
        for content_data in contents:
            content = StructuredContent(
                module_name=content_data['module_name'],
                unit_name=content_data.get('unit_name', 'General'),
                topic_name=content_data['topic_name'],
                structured_markdown=content_data['structured_markdown'],
                created_by=ObjectId(created_by),
                original_paragraphs=content_data.get('original_paragraphs', []),
                metadata=content_data.get('metadata', {})
            )
            created_contents.append(content)
        
        try:
            documents = [c.to_dict() for c in created_contents]
            self.db.structured_contents.insert_many(documents)
            logger.info(f"Inserted {len(created_contents)} content items")
            return created_contents
        except Exception as e:
            logger.error(f"Failed to insert contents: {e}")
            raise ContentStorageError(f"Failed to insert contents: {str(e)}", 500)
    
    def get_content_by_id(self, content_id: str) -> Optional[StructuredContent]:
        """Get a single content item by ID."""
        if self.db is None:
            return None
        
        try:
            data = self.db.structured_contents.find_one({'_id': ObjectId(content_id)})
            if data:
                return StructuredContent.from_dict(data)
            return None
        except Exception as e:
            logger.error(f"Failed to get content: {e}")
            return None
    
    def get_contents_by_module(
        self, 
        module_name: str,
        approved_only: bool = False
    ) -> List[StructuredContent]:
        """Get all contents for a module."""
        if self.db is None:
            return []
        
        query = {'module_name': module_name}
        if approved_only:
            query['approved'] = True
        
        try:
            cursor = self.db.structured_contents.find(query).sort([
                ('unit_name', ASCENDING),
                ('topic_name', ASCENDING)
            ])
            return [StructuredContent.from_dict(doc) for doc in cursor]
        except Exception as e:
            logger.error(f"Failed to get module contents: {e}")
            return []
    
    def get_unapproved_contents_by_module(
        self, 
        module_name: str
    ) -> List[StructuredContent]:
        """Get all unapproved contents for a module."""
        if self.db is None:
            return []
        
        query = {
            'module_name': module_name,
            'approved': False
        }
        
        try:
            cursor = self.db.structured_contents.find(query).sort([
                ('unit_name', ASCENDING),
                ('topic_name', ASCENDING)
            ])
            return [StructuredContent.from_dict(doc) for doc in cursor]
        except Exception as e:
            logger.error(f"Failed to get unapproved module contents: {e}")
            return []
    
    def get_contents_by_topic(
        self,
        module_name: str,
        unit_name: str,
        topic_name: str
    ) -> Optional[StructuredContent]:
        """Get content for a specific topic."""
        if self.db is None:
            return None
        
        try:
            data = self.db.structured_contents.find_one({
                'module_name': module_name,
                'unit_name': unit_name,
                'topic_name': topic_name
            })
            if data:
                return StructuredContent.from_dict(data)
            return None
        except Exception as e:
            logger.error(f"Failed to get topic content: {e}")
            return None
    
    def update_content(
        self,
        content_id: str,
        updates: Dict[str, Any]
    ) -> Optional[StructuredContent]:
        """Update a content item."""
        if self.db is None:
            return None
        
        updates['updated_at'] = datetime.utcnow()
        
        try:
            result = self.db.structured_contents.find_one_and_update(
                {'_id': ObjectId(content_id)},
                {'$set': updates},
                return_document=True
            )
            if result:
                return StructuredContent.from_dict(result)
            return None
        except Exception as e:
            logger.error(f"Failed to update content: {e}")
            return None
    
    def approve_content(
        self,
        content_id: str,
        reviewer_id: str
    ) -> Optional[StructuredContent]:
        """Approve a content item."""
        return self.update_content(content_id, {
            'approved': True,
            'status': ContentStatus.APPROVED.value,
            'reviewed_by': ObjectId(reviewer_id),
            'approved_at': datetime.utcnow()
        })
    
    def approve_content_simple(
        self,
        content_id: str
    ) -> Optional[StructuredContent]:
        """Approve a content item (simple version without reviewer tracking)."""
        return self.update_content(content_id, {
            'approved': True,
            'status': ContentStatus.APPROVED.value,
            'approved_at': datetime.utcnow()
        })
    
    def delete_content(self, content_id: str) -> bool:
        """Delete a content item."""
        if self.db is None:
            return False
        
        try:
            result = self.db.structured_contents.delete_one({'_id': ObjectId(content_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete content: {e}")
            return False
    
    # ==================== Module Content CRUD ====================
    
    def create_module(
        self,
        module_name: str,
        created_by: str,
        upload_id: Optional[str] = None,
        description: Optional[str] = None,
        units: Optional[List[Dict]] = None
    ) -> ModuleContent:
        """Create a new module content entry."""
        if self.db is None:
            raise ContentStorageError("Database not connected", 500)
        
        self._ensure_indexes()
        
        module = ModuleContent(
            module_name=module_name,
            created_by=ObjectId(created_by),
            upload_id=upload_id,
            description=description,
            units=units or []
        )
        
        try:
            self.db.module_contents.insert_one(module.to_dict())
            logger.info(f"Created module: {module_name}")
            return module
        except DuplicateKeyError:
            raise ContentStorageError(f"Module '{module_name}' already exists", 409)
        except Exception as e:
            logger.error(f"Failed to create module: {e}")
            raise ContentStorageError(f"Failed to create module: {str(e)}", 500)
    
    def get_module(self, module_name: str) -> Optional[ModuleContent]:
        """Get a module by name."""
        if self.db is None:
            return None
        
        try:
            data = self.db.module_contents.find_one({'module_name': module_name})
            if data:
                return ModuleContent.from_dict(data)
            return None
        except Exception as e:
            logger.error(f"Failed to get module: {e}")
            return None
    
    def get_all_modules(
        self,
        created_by: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[ModuleContent]:
        """Get all modules with optional filters."""
        if self.db is None:
            return []
        
        query = {}
        if created_by:
            query['created_by'] = ObjectId(created_by)
        if status:
            query['status'] = status
        
        try:
            cursor = self.db.module_contents.find(query).sort('created_at', DESCENDING)
            return [ModuleContent.from_dict(doc) for doc in cursor]
        except Exception as e:
            logger.error(f"Failed to get modules: {e}")
            return []
    
    def update_module_stats(self, module_name: str) -> Optional[ModuleContent]:
        """Update module statistics (total topics, approved count)."""
        if self.db is None:
            return None
        
        try:
            # Count topics
            total = self.db.structured_contents.count_documents({'module_name': module_name})
            approved = self.db.structured_contents.count_documents({
                'module_name': module_name,
                'approved': True
            })
            
            return self.update_module(module_name, {
                'total_topics': total,
                'approved_topics': approved
            })
        except Exception as e:
            logger.error(f"Failed to update module stats: {e}")
            return None
    
    def update_module(
        self,
        module_name: str,
        updates: Dict[str, Any]
    ) -> Optional[ModuleContent]:
        """Update a module."""
        if self.db is None:
            return None
        
        updates['updated_at'] = datetime.utcnow()
        
        try:
            result = self.db.module_contents.find_one_and_update(
                {'module_name': module_name},
                {'$set': updates},
                return_document=True
            )
            if result:
                return ModuleContent.from_dict(result)
            return None
        except Exception as e:
            logger.error(f"Failed to update module: {e}")
            return None
    
    # ==================== Utility Functions ====================
    
    def get_student_content(
        self,
        module_name: str,
        unit_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get approved content for student access.
        
        Only returns published, approved content.
        """
        if self.db is None:
            return []
        
        query = {
            'module_name': module_name,
            'approved': True,
            'status': ContentStatus.PUBLISHED.value
        }
        if unit_name:
            query['unit_name'] = unit_name
        
        try:
            cursor = self.db.structured_contents.find(
                query,
                {'original_paragraphs': 0}  # Exclude original paragraphs for students
            ).sort([
                ('unit_name', ASCENDING),
                ('topic_name', ASCENDING)
            ])
            
            return [StructuredContent.from_dict(doc).to_response_dict() for doc in cursor]
        except Exception as e:
            logger.error(f"Failed to get student content: {e}")
            return []
    
    def search_content(
        self,
        search_term: str,
        module_name: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search content by text."""
        if self.db is None:
            return []
        
        query = {
            '$text': {'$search': search_term}
        }
        if module_name:
            query['module_name'] = module_name
        
        try:
            # Create text index if not exists
            self.db.structured_contents.create_index([
                ('topic_name', 'text'),
                ('structured_markdown', 'text')
            ])
            
            cursor = self.db.structured_contents.find(
                query,
                {'score': {'$meta': 'textScore'}}
            ).sort([('score', {'$meta': 'textScore'})]).limit(limit)
            
            return [StructuredContent.from_dict(doc).to_response_dict() for doc in cursor]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get_content_stats(self) -> Dict[str, Any]:
        """Get overall content statistics."""
        if self.db is None:
            return {}
        
        try:
            total_contents = self.db.structured_contents.count_documents({})
            approved_contents = self.db.structured_contents.count_documents({'approved': True})
            total_modules = self.db.module_contents.count_documents({})
            
            # Contents by status
            status_pipeline = [
                {'$group': {'_id': '$status', 'count': {'$sum': 1}}}
            ]
            status_counts = {doc['_id']: doc['count'] 
                          for doc in self.db.structured_contents.aggregate(status_pipeline)}
            
            return {
                'total_contents': total_contents,
                'approved_contents': approved_contents,
                'pending_contents': total_contents - approved_contents,
                'total_modules': total_modules,
                'by_status': status_counts
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}
    
    # ==================== Enrollment Operations ====================
    
    def enroll_student(
        self,
        student_id: str,
        module_name: str
    ) -> Enrollment:
        """
        Enroll a student in a module.
        
        Args:
            student_id: Student user ID
            module_name: Name of the module
            
        Returns:
            The created Enrollment object
            
        Raises:
            ContentStorageError: If enrollment fails or already exists
        """
        if self.db is None:
            raise ContentStorageError("Database not connected", 500)
        
        self._ensure_indexes()
        
        # Check if already enrolled
        existing = self.db.enrollments.find_one({
            'student_id': ObjectId(student_id),
            'module_name': module_name
        })
        
        if existing:
            raise ContentStorageError(
                f"Student is already enrolled in module '{module_name}'",
                409
            )
        
        # Verify module exists
        module = self.get_module(module_name)
        if not module:
            raise ContentStorageError(
                f"Module '{module_name}' not found",
                404
            )
        
        # Create enrollment
        enrollment = Enrollment(
            student_id=ObjectId(student_id),
            module_name=module_name
        )
        
        try:
            self.db.enrollments.insert_one(enrollment.to_dict())
            logger.info(f"Student {student_id} enrolled in module: {module_name}")
            return enrollment
        except Exception as e:
            logger.error(f"Failed to create enrollment: {e}")
            raise ContentStorageError(f"Failed to create enrollment: {str(e)}", 500)
    
    def is_student_enrolled(
        self,
        student_id: str,
        module_name: str
    ) -> bool:
        """Check if a student is enrolled in a module."""
        if self.db is None:
            return False
        
        try:
            enrollment = self.db.enrollments.find_one({
                'student_id': ObjectId(student_id),
                'module_name': module_name
            })
            return enrollment is not None
        except Exception as e:
            logger.error(f"Failed to check enrollment: {e}")
            return False
    
    def get_student_enrollments(
        self,
        student_id: str
    ) -> List[Enrollment]:
        """Get all modules a student is enrolled in."""
        if self.db is None:
            return []
        
        try:
            cursor = self.db.enrollments.find({
                'student_id': ObjectId(student_id)
            }).sort('enrolled_at', DESCENDING)
            return [Enrollment.from_dict(doc) for doc in cursor]
        except Exception as e:
            logger.error(f"Failed to get student enrollments: {e}")
            return []
    
    def get_module_enrollments(
        self,
        module_name: str
    ) -> List[Enrollment]:
        """Get all students enrolled in a module."""
        if self.db is None:
            return []
        
        try:
            cursor = self.db.enrollments.find({
                'module_name': module_name
            }).sort('enrolled_at', DESCENDING)
            return [Enrollment.from_dict(doc) for doc in cursor]
        except Exception as e:
            logger.error(f"Failed to get module enrollments: {e}")
            return []


# Singleton instance
content_storage = ContentStorage()


# Convenience function
def insert_structured_content(
    module_name: str,
    unit_name: str,
    topic_name: str,
    structured_markdown: str,
    created_by: str,
    original_paragraphs: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> StructuredContent:
    """
    Insert structured content into MongoDB.
    
    Convenience function for direct use.
    """
    return content_storage.insert_structured_content(
        module_name=module_name,
        unit_name=unit_name,
        topic_name=topic_name,
        structured_markdown=structured_markdown,
        created_by=created_by,
        original_paragraphs=original_paragraphs,
        metadata=metadata
    )




