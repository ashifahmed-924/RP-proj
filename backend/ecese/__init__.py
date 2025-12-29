"""
ECESE - Education Content Extraction and Structuring Engine

This module provides functionality for:
- Teacher uploads (textbook PDF, teacher guide PDF, module name)
- Extracting skeleton structure from Teacher Guide
- Extracting paragraphs from Textbook
- Semantic scope guard for curriculum alignment
- Content structuring with controlled AI (Groq/LLaMA)
- Persistent storage in MongoDB
- Mapping textbook content to curriculum skeleton
"""

from .ecese_service import ECESEService
from .skeleton_extractor import SkeletonExtractor
from .paragraph_extractor import ParagraphExtractor
from .scope_guard import SemanticScopeGuard, ScopeGuardLite, create_scope_guard
from .content_structurer import ContentStructurer, ContentStructurerLite, create_content_structurer
from .content_storage import ContentStorage, content_storage, insert_structured_content
from .models.structured_content import StructuredContent, ModuleContent, ContentStatus

__all__ = [
    'ECESEService', 
    'SkeletonExtractor', 
    'ParagraphExtractor',
    'SemanticScopeGuard',
    'ScopeGuardLite',
    'create_scope_guard',
    'ContentStructurer',
    'ContentStructurerLite',
    'create_content_structurer',
    'ContentStorage',
    'content_storage',
    'insert_structured_content',
    'StructuredContent',
    'ModuleContent',
    'ContentStatus'
]

