"""
ECESE Pydantic Models

Data models for the Education Content Extraction and Structuring Engine.
"""

from datetime import datetime
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field
from enum import Enum


class UploadStatus(str, Enum):
    """Status of an upload."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ModuleUpload(BaseModel):
    """Model for module upload metadata."""
    id: str = Field(..., description="Unique upload ID")
    module_name: str = Field(..., description="Name of the module (e.g., 'History')")
    textbook_path: str = Field(..., description="Path to uploaded textbook PDF")
    teacher_guide_path: str = Field(..., description="Path to uploaded teacher guide PDF")
    status: UploadStatus = Field(default=UploadStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    skeleton: Optional[Dict[str, List[str]]] = Field(default=None, description="Extracted skeleton structure")
    error_message: Optional[str] = None


class UploadResponse(BaseModel):
    """Response model for upload endpoint."""
    success: bool
    message: str
    upload_id: str
    module_name: str
    textbook_filename: str
    teacher_guide_filename: str
    textbook_path: str
    teacher_guide_path: str


class SkeletonResponse(BaseModel):
    """Response model for skeleton extraction."""
    success: bool
    upload_id: str
    module_name: str
    skeleton: Dict[str, List[str]]
    total_units: int
    total_lessons: int


class HeaderInfo(BaseModel):
    """Information about an extracted header."""
    text: str
    font_size: float
    page_number: int
    block_index: int
    level: int  # 1 = Unit, 2 = Lesson, 3 = Sub-lesson


class ExtractionResult(BaseModel):
    """Result of PDF text extraction."""
    headers: List[HeaderInfo]
    skeleton: Dict[str, List[str]]
    raw_text: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    error: str
    details: Optional[str] = None

