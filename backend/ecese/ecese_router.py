"""
ECESE Router Module

FastAPI router for Education Content Extraction and Structuring Engine.
Provides endpoints for teacher uploads and skeleton extraction.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional
import os

from .ecese_service import ecese_service
from .ecese_models import (
    UploadResponse, 
    SkeletonResponse, 
    ErrorResponse,
    UploadStatus
)
from .paragraph_extractor import ParagraphExtractor
from .scope_guard import create_scope_guard
from .content_structurer import create_content_structurer, structure_content
from .content_storage import content_storage, ContentStorageError
from .models.structured_content import ContentStatus


router = APIRouter(prefix="/ecese", tags=["ECESE"])


@router.post(
    "/upload",
    response_model=UploadResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Upload textbook and teacher guide PDFs",
    description="""
    Upload a textbook PDF and teacher guide PDF for a specific module.
    
    The teacher guide will be used to extract the curriculum skeleton (Unit/Lesson structure).
    The textbook will be mapped to this skeleton in subsequent processing.
    
    **Required:**
    - textbook: PDF file of the textbook
    - teacher_guide: PDF file of the teacher guide
    - module_name: Name of the module (e.g., "History", "Mathematics")
    """
)
async def upload_module(
    textbook: UploadFile = File(..., description="Textbook PDF file"),
    teacher_guide: UploadFile = File(..., description="Teacher Guide PDF file"),
    module_name: str = Form(..., description="Module name (e.g., 'History')")
):
    """
    Upload textbook and teacher guide PDFs for a module.
    
    This endpoint:
    1. Validates the uploaded files are PDFs
    2. Stores them temporarily on disk
    3. Returns confirmation with file paths and upload ID
    """
    
    # Validate file types
    if not textbook.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Textbook must be a PDF file"
        )
    
    if not teacher_guide.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Teacher guide must be a PDF file"
        )
    
    # Validate module name
    module_name = module_name.strip()
    if not module_name:
        raise HTTPException(
            status_code=400,
            detail="Module name cannot be empty"
        )
    
    try:
        # Read file contents
        textbook_content = await textbook.read()
        teacher_guide_content = await teacher_guide.read()
        
        # Validate file sizes (max 50MB each)
        max_size = 50 * 1024 * 1024  # 50MB
        if len(textbook_content) > max_size:
            raise HTTPException(
                status_code=400,
                detail="Textbook file exceeds maximum size of 50MB"
            )
        if len(teacher_guide_content) > max_size:
            raise HTTPException(
                status_code=400,
                detail="Teacher guide file exceeds maximum size of 50MB"
            )
        
        # Process upload
        upload = await ecese_service.process_upload(
            module_name=module_name,
            textbook_content=textbook_content,
            textbook_filename=textbook.filename,
            teacher_guide_content=teacher_guide_content,
            teacher_guide_filename=teacher_guide.filename
        )
        
        return UploadResponse(
            success=True,
            message=f"Successfully uploaded files for module: {module_name}",
            upload_id=upload.id,
            module_name=upload.module_name,
            textbook_filename=textbook.filename,
            teacher_guide_filename=teacher_guide.filename,
            textbook_path=upload.textbook_path,
            teacher_guide_path=upload.teacher_guide_path
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process upload: {str(e)}"
        )


@router.post(
    "/extract-skeleton/{upload_id}",
    response_model=SkeletonResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Extract skeleton from teacher guide",
    description="""
    Extract the curriculum skeleton (Unit/Lesson structure) from the uploaded teacher guide.
    
    This uses PyMuPDF to analyze font sizes and identify headers.
    Headers with font size > 12 are considered section headers.
    
    **Returns:**
    - Hierarchical structure with Units containing Lessons
    - Example: {"Unit 1": ["Lesson 1.1", "Lesson 1.2"], "Unit 2": ["Lesson 2.1"]}
    """
)
async def extract_skeleton(upload_id: str):
    """
    Extract skeleton structure from an uploaded teacher guide.
    
    This establishes the "Scope Authority" - the official curriculum structure
    that content will be mapped to.
    """
    
    # Get upload
    upload = ecese_service.get_upload(upload_id)
    if not upload:
        raise HTTPException(
            status_code=404,
            detail=f"Upload not found: {upload_id}"
        )
    
    # Check if already extracted
    if upload.skeleton:
        stats = ecese_service.get_skeleton_stats(upload.skeleton)
        return SkeletonResponse(
            success=True,
            upload_id=upload_id,
            module_name=upload.module_name,
            skeleton=upload.skeleton,
            total_units=stats["total_units"],
            total_lessons=stats["total_lessons"]
        )
    
    try:
        # Extract skeleton
        skeleton = ecese_service.extract_skeleton(upload_id)
        stats = ecese_service.get_skeleton_stats(skeleton)
        
        return SkeletonResponse(
            success=True,
            upload_id=upload_id,
            module_name=upload.module_name,
            skeleton=skeleton,
            total_units=stats["total_units"],
            total_lessons=stats["total_lessons"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract skeleton: {str(e)}"
        )


@router.get(
    "/upload/{upload_id}",
    summary="Get upload details",
    description="Retrieve details of a specific upload including its processing status."
)
async def get_upload(upload_id: str):
    """Get details of a specific upload."""
    
    upload = ecese_service.get_upload(upload_id)
    if not upload:
        raise HTTPException(
            status_code=404,
            detail=f"Upload not found: {upload_id}"
        )
    
    return {
        "id": upload.id,
        "module_name": upload.module_name,
        "status": upload.status.value,
        "textbook_path": upload.textbook_path,
        "teacher_guide_path": upload.teacher_guide_path,
        "skeleton": upload.skeleton,
        "created_at": upload.created_at.isoformat(),
        "updated_at": upload.updated_at.isoformat(),
        "error_message": upload.error_message
    }


@router.get(
    "/uploads",
    summary="List all uploads",
    description="Get a list of all module uploads."
)
async def list_uploads():
    """List all uploads."""
    
    uploads = ecese_service.get_all_uploads()
    
    return {
        "total": len(uploads),
        "uploads": [
            {
                "id": u.id,
                "module_name": u.module_name,
                "status": u.status.value,
                "created_at": u.created_at.isoformat(),
                "has_skeleton": u.skeleton is not None
            }
            for u in uploads
        ]
    }


@router.delete(
    "/upload/{upload_id}",
    summary="Delete an upload",
    description="Delete an upload and its associated files."
)
async def delete_upload(upload_id: str):
    """Delete an upload and its files."""
    
    deleted = ecese_service.delete_upload(upload_id)
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Upload not found: {upload_id}"
        )
    
    return {
        "success": True,
        "message": f"Upload {upload_id} deleted successfully"
    }


@router.post(
    "/test-extraction",
    summary="Test skeleton extraction on existing file",
    description="Test the skeleton extraction on an existing PDF file path."
)
async def test_extraction(file_path: str = Form(...)):
    """
    Test skeleton extraction on an existing file.
    Useful for debugging and testing the extraction logic.
    """
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {file_path}"
        )
    
    try:
        from .skeleton_extractor import SkeletonExtractor
        
        extractor = SkeletonExtractor()
        
        # Get text blocks for debugging
        text_blocks = extractor.extract_text_blocks(file_path)
        headers = extractor.identify_headers(text_blocks)
        skeleton = extractor.build_skeleton(headers)
        stats = extractor.get_extraction_stats(skeleton)
        
        return {
            "success": True,
            "file_path": file_path,
            "total_text_blocks": len(text_blocks),
            "total_headers_found": len(headers),
            "skeleton": skeleton,
            "stats": stats,
            "sample_headers": [
                {
                    "text": h.text[:50],
                    "font_size": h.font_size,
                    "page": h.page_number
                }
                for h in headers[:20]  # First 20 headers
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {str(e)}"
        )


# ==================== STEP 3: Paragraph Extraction ====================

@router.post(
    "/extract-paragraphs/{upload_id}",
    summary="Extract paragraphs from textbook",
    description="""
    Extract paragraph-level content from the uploaded textbook PDF.
    
    This extracts the "Flesh" - raw content that will be mapped to 
    the curriculum skeleton via semantic matching.
    
    - Splits content into paragraphs
    - Removes very short paragraphs (<30 characters)
    - Filters out page numbers, headers, and other non-content
    """
)
async def extract_paragraphs(upload_id: str):
    """Extract paragraphs from a textbook PDF."""
    
    upload = ecese_service.get_upload(upload_id)
    if not upload:
        raise HTTPException(
            status_code=404,
            detail=f"Upload not found: {upload_id}"
        )
    
    try:
        paragraphs = ecese_service.extract_paragraphs(upload_id)
        stats = ecese_service.get_paragraph_stats(paragraphs)
        
        return {
            "success": True,
            "upload_id": upload_id,
            "module_name": upload.module_name,
            "total_paragraphs": len(paragraphs),
            "stats": stats,
            "sample_paragraphs": paragraphs[:10],  # First 10 paragraphs
            "paragraphs": paragraphs  # Full list
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract paragraphs: {str(e)}"
        )


@router.post(
    "/test-paragraphs",
    summary="Test paragraph extraction on existing file",
    description="Test paragraph extraction on an existing PDF file path."
)
async def test_paragraph_extraction(
    file_path: str = Form(...),
    min_length: int = Form(30)
):
    """Test paragraph extraction on an existing file."""
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {file_path}"
        )
    
    try:
        extractor = ParagraphExtractor(min_length=min_length)
        paragraphs = extractor.extract_paragraphs(file_path)
        stats = extractor.get_extraction_stats(paragraphs)
        
        return {
            "success": True,
            "file_path": file_path,
            "min_length": min_length,
            "total_paragraphs": len(paragraphs),
            "stats": stats,
            "sample_paragraphs": [
                {"index": i, "text": p[:200] + "..." if len(p) > 200 else p, "length": len(p)}
                for i, p in enumerate(paragraphs[:20])
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {str(e)}"
        )


# ==================== STEP 4: Semantic Scope Guard ====================

@router.post(
    "/apply-scope-guard/{upload_id}",
    summary="Apply semantic scope guard",
    description="""
    Apply semantic scope guard to match textbook paragraphs to curriculum topics.
    
    **CORE LOGIC:**
    - Uses sentence-transformers with 'all-MiniLM-L6-v2' model
    - Converts topics and paragraphs to embeddings
    - Matches via cosine similarity
    - Keeps paragraphs ONLY if similarity > threshold
    - Logs rejected paragraphs as "out of scope"
    
    **Returns:**
    - Structured JSON mapping topics to paragraphs
    - Statistics on in-scope vs out-of-scope content
    """
)
async def apply_scope_guard(
    upload_id: str,
    similarity_threshold: float = 0.4
):
    """Apply semantic scope guard to content."""
    
    upload = ecese_service.get_upload(upload_id)
    if not upload:
        raise HTTPException(
            status_code=404,
            detail=f"Upload not found: {upload_id}"
        )
    
    try:
        result = ecese_service.apply_scope_guard(upload_id, similarity_threshold)
        
        return {
            "success": True,
            "upload_id": upload_id,
            "module_name": upload.module_name,
            "similarity_threshold": similarity_threshold,
            **result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to apply scope guard: {str(e)}"
        )


@router.post(
    "/test-scope-guard",
    summary="Test scope guard matching",
    description="Test semantic scope guard with custom topics and paragraphs."
)
async def test_scope_guard(
    topics: str = Form(..., description="Comma-separated list of topics"),
    paragraphs: str = Form(..., description="Paragraphs separated by |||"),
    similarity_threshold: float = Form(0.4)
):
    """Test scope guard with custom input."""
    
    topic_list = [t.strip() for t in topics.split(",") if t.strip()]
    paragraph_list = [p.strip() for p in paragraphs.split("|||") if p.strip()]
    
    if not topic_list:
        raise HTTPException(status_code=400, detail="No topics provided")
    if not paragraph_list:
        raise HTTPException(status_code=400, detail="No paragraphs provided")
    
    try:
        guard = create_scope_guard(
            use_semantic=True,
            similarity_threshold=similarity_threshold
        )
        result = guard.guard_content(topic_list, paragraph_list)
        
        return {
            "success": True,
            "topics": topic_list,
            "paragraph_count": len(paragraph_list),
            "similarity_threshold": similarity_threshold,
            "structured_content": result.structured_content,
            "in_scope_count": result.in_scope_count,
            "out_of_scope_count": result.out_of_scope_count,
            "topic_coverage": result.topic_coverage,
            "average_similarity": result.average_similarity,
            "rejected_paragraphs": [
                {"paragraph": p[:100] + "...", "best_score": round(s, 3)}
                for p, s in result.rejected_paragraphs
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scope guard failed: {str(e)}"
        )


# ==================== Complete Processing Pipeline ====================

@router.post(
    "/process/{upload_id}",
    summary="Complete processing pipeline",
    description="""
    Run the complete ECESE processing pipeline:
    
    1. Extract skeleton from teacher guide (Scope Authority)
    2. Extract paragraphs from textbook (Raw Content)
    3. Apply semantic scope guard (Content Alignment)
    
    Returns the fully structured, curriculum-aligned content.
    """
)
async def process_module(
    upload_id: str,
    similarity_threshold: float = 0.4
):
    """Run complete processing pipeline."""
    
    upload = ecese_service.get_upload(upload_id)
    if not upload:
        raise HTTPException(
            status_code=404,
            detail=f"Upload not found: {upload_id}"
        )
    
    try:
        result = ecese_service.process_complete_module(upload_id, similarity_threshold)
        
        return {
            "success": True,
            **result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )


# ==================== STEP 5: Content Structuring (Controlled AI) ====================

@router.post(
    "/structure-topic",
    summary="Structure content for a single topic",
    description="""
    Transform raw paragraphs into structured Markdown notes using Groq AI.
    
    ⚠️ This is TRANSFORMATION, not generation:
    - ONLY restructures the provided text
    - Does NOT add new information
    - Does NOT introduce examples not in the original
    
    Uses llama3-8b-8192 model with controlled system prompt.
    
    **Required:** Groq API key
    """
)
async def structure_topic(
    topic: str = Form(..., description="Topic/lesson name"),
    paragraphs: str = Form(..., description="Paragraphs separated by |||"),
    groq_api_key: str = Form(..., description="Groq API key")
):
    """Structure content for a single topic using controlled AI."""
    
    paragraph_list = [p.strip() for p in paragraphs.split("|||") if p.strip()]
    
    if not paragraph_list:
        raise HTTPException(status_code=400, detail="No paragraphs provided")
    
    if not groq_api_key:
        raise HTTPException(status_code=400, detail="Groq API key is required")
    
    try:
        result = ecese_service.structure_topic_content(
            topic=topic,
            paragraphs=paragraph_list,
            groq_api_key=groq_api_key
        )
        
        return {
            "success": True,
            **result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Structuring failed: {str(e)}"
        )


@router.post(
    "/structure-all/{upload_id}",
    summary="Structure all topics from an upload",
    description="""
    Run the complete content structuring pipeline:
    
    1. Apply scope guard to filter content
    2. Structure each topic with controlled AI
    3. Generate full Markdown document
    
    ⚠️ This uses Groq AI for TRANSFORMATION only - no new content is generated.
    
    **Required:** Groq API key
    """
)
async def structure_all_topics(
    upload_id: str,
    groq_api_key: str = Form(..., description="Groq API key"),
    similarity_threshold: float = Form(0.4, description="Scope guard threshold")
):
    """Structure all topics from an upload using controlled AI."""
    
    upload = ecese_service.get_upload(upload_id)
    if not upload:
        raise HTTPException(
            status_code=404,
            detail=f"Upload not found: {upload_id}"
        )
    
    if not groq_api_key:
        raise HTTPException(status_code=400, detail="Groq API key is required")
    
    try:
        result = ecese_service.structure_all_topics(
            upload_id=upload_id,
            groq_api_key=groq_api_key,
            similarity_threshold=similarity_threshold
        )
        
        return {
            "success": True,
            **result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Structuring failed: {str(e)}"
        )


@router.post(
    "/test-structure",
    summary="Test content structuring",
    description="""
    Test the content structuring function with custom input.
    
    Useful for testing the AI transformation before running on full uploads.
    """
)
async def test_structure(
    topic: str = Form("Test Topic", description="Topic name"),
    text: str = Form(..., description="Text to structure"),
    groq_api_key: str = Form(..., description="Groq API key"),
    model: str = Form("llama3-8b-8192", description="Model to use")
):
    """Test content structuring with custom input."""
    
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    if not groq_api_key:
        raise HTTPException(status_code=400, detail="Groq API key is required")
    
    try:
        from .content_structurer import ContentStructurer
        
        structurer = ContentStructurer(api_key=groq_api_key, model=model)
        
        # Split text into paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if not paragraphs:
            paragraphs = [text]
        
        result = structurer.structure_content(topic, paragraphs)
        
        return {
            "success": True,
            "topic": result.topic,
            "input_paragraphs": len(paragraphs),
            "word_count_original": result.word_count_original,
            "word_count_structured": result.word_count_structured,
            "compression_ratio": f"{result.word_count_structured/result.word_count_original:.1%}" if result.word_count_original > 0 else "N/A",
            "model_used": result.model_used,
            "tokens_used": result.tokens_used,
            "structured_markdown": result.structured_markdown
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Structuring failed: {str(e)}"
        )


# ==================== STEP 6: Content Storage (MongoDB) ====================

@router.post(
    "/content/save",
    summary="Save structured content to MongoDB",
    description="""
    Save structured educational content to the database for student access.
    
    **Fields:**
    - module_name: Name of the module (e.g., "History Grade 10")
    - unit_name: Name of the unit
    - topic_name: Name of the topic/lesson
    - structured_markdown: The AI-structured content
    - created_by: Teacher ID who created the content
    """
)
async def save_content(
    module_name: str = Form(..., description="Module name"),
    unit_name: str = Form(..., description="Unit name"),
    topic_name: str = Form(..., description="Topic/lesson name"),
    structured_markdown: str = Form(..., description="Structured Markdown content"),
    created_by: str = Form(..., description="Teacher ID"),
    original_paragraphs: str = Form("", description="Original paragraphs (||| separated)")
):
    """Save structured content to MongoDB."""
    
    paragraphs = [p.strip() for p in original_paragraphs.split("|||") if p.strip()] if original_paragraphs else []
    
    try:
        content = content_storage.insert_structured_content(
            module_name=module_name,
            unit_name=unit_name,
            topic_name=topic_name,
            structured_markdown=structured_markdown,
            created_by=created_by,
            original_paragraphs=paragraphs,
            metadata={
                'word_count': len(structured_markdown.split()),
                'paragraph_count': len(paragraphs)
            }
        )
        
        return {
            "success": True,
            "message": "Content saved successfully",
            "content": content.to_response_dict()
        }
        
    except ContentStorageError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save content: {str(e)}")


@router.post(
    "/content/save-batch",
    summary="Save multiple contents at once",
    description="Save multiple structured contents in a batch operation."
)
async def save_content_batch(
    contents: str = Form(..., description="JSON array of content objects"),
    created_by: str = Form(..., description="Teacher ID")
):
    """Save multiple contents at once."""
    
    import json
    
    try:
        content_list = json.loads(contents)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for contents")
    
    if not isinstance(content_list, list):
        raise HTTPException(status_code=400, detail="Contents must be an array")
    
    try:
        saved_contents = content_storage.insert_multiple_contents(content_list, created_by)
        
        return {
            "success": True,
            "message": f"Saved {len(saved_contents)} content items",
            "count": len(saved_contents),
            "content_ids": [str(c._id) for c in saved_contents]
        }
        
    except ContentStorageError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save contents: {str(e)}")


@router.get(
    "/content/stats",
    summary="Get content statistics",
    description="Get overall statistics about stored content."
)
async def get_content_stats():
    """Get content statistics."""
    
    stats = content_storage.get_content_stats()
    
    return {
        "success": True,
        "stats": stats
    }


@router.get(
    "/content/{content_id}",
    summary="Get content by ID",
    description="Retrieve a specific content item by its ID."
)
async def get_content(content_id: str):
    """Get content by ID."""
    
    content = content_storage.get_content_by_id(content_id)
    
    if not content:
        raise HTTPException(status_code=404, detail=f"Content not found: {content_id}")
    
    return {
        "success": True,
        "content": content.to_response_dict()
    }


@router.get(
    "/content/module/{module_name}",
    summary="Get all contents for a module",
    description="Retrieve all structured contents for a specific module."
)
async def get_module_contents(
    module_name: str,
    approved_only: bool = False
):
    """Get all contents for a module."""
    
    contents = content_storage.get_contents_by_module(module_name, approved_only)
    
    return {
        "success": True,
        "module_name": module_name,
        "count": len(contents),
        "contents": [c.to_response_dict() for c in contents]
    }


@router.get(
    "/review/{module_name}",
    summary="Get unapproved content for review",
    description="Returns all structured content for the module where approved = false."
)
async def review_module_content(module_name: str):
    """Get all unapproved content for a module for human review."""
    
    contents = content_storage.get_unapproved_contents_by_module(module_name)
    
    return {
        "success": True,
        "module_name": module_name,
        "count": len(contents),
        "contents": [c.to_response_dict() for c in contents]
    }


@router.put(
    "/content/{content_id}/approve",
    summary="Approve content",
    description="Approve a content item (teacher/admin only)."
)
async def approve_content(
    content_id: str,
    reviewer_id: str = Form(..., description="Reviewer's user ID")
):
    """Approve a content item."""
    
    content = content_storage.approve_content(content_id, reviewer_id)
    
    if not content:
        raise HTTPException(status_code=404, detail=f"Content not found: {content_id}")
    
    return {
        "success": True,
        "message": "Content approved successfully",
        "content": content.to_response_dict()
    }


@router.post(
    "/approve/{content_id}",
    summary="Approve content (simple)",
    description="Sets approved = true for a content item."
)
async def approve_content_simple(content_id: str):
    """Approve a content item (simple version)."""
    
    content = content_storage.approve_content_simple(content_id)
    
    if not content:
        raise HTTPException(status_code=404, detail=f"Content not found: {content_id}")
    
    return {
        "success": True,
        "message": "Content approved successfully",
        "content": content.to_response_dict()
    }


@router.put(
    "/content/{content_id}",
    summary="Update content",
    description="Update a structured content item."
)
async def update_content(
    content_id: str,
    structured_markdown: str = Form(None, description="Updated Markdown content"),
    status: str = Form(None, description="New status")
):
    """Update content."""
    
    updates = {}
    if structured_markdown:
        updates['structured_markdown'] = structured_markdown
    if status:
        updates['status'] = status
    
    if not updates:
        raise HTTPException(status_code=400, detail="No updates provided")
    
    content = content_storage.update_content(content_id, updates)
    
    if not content:
        raise HTTPException(status_code=404, detail=f"Content not found: {content_id}")
    
    return {
        "success": True,
        "message": "Content updated successfully",
        "content": content.to_response_dict()
    }


@router.delete(
    "/content/{content_id}",
    summary="Delete content",
    description="Delete a structured content item."
)
async def delete_content(content_id: str):
    """Delete content."""
    
    deleted = content_storage.delete_content(content_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Content not found: {content_id}")
    
    return {
        "success": True,
        "message": f"Content {content_id} deleted successfully"
    }


# ==================== Module Management ====================

@router.post(
    "/module",
    summary="Create a module",
    description="Create a new module entry to organize content."
)
async def create_module(
    module_name: str = Form(..., description="Module name"),
    created_by: str = Form(..., description="Teacher ID"),
    description: str = Form(None, description="Module description"),
    upload_id: str = Form(None, description="Associated upload ID")
):
    """Create a new module."""
    
    try:
        module = content_storage.create_module(
            module_name=module_name,
            created_by=created_by,
            description=description,
            upload_id=upload_id
        )
        
        return {
            "success": True,
            "message": f"Module '{module_name}' created successfully",
            "module": module.to_response_dict()
        }
        
    except ContentStorageError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create module: {str(e)}")


@router.get(
    "/modules",
    summary="List all modules",
    description="Get a list of all modules."
)
async def list_modules(
    created_by: str = None,
    status: str = None
):
    """List all modules."""
    
    modules = content_storage.get_all_modules(created_by=created_by, status=status)
    
    return {
        "success": True,
        "count": len(modules),
        "modules": [m.to_response_dict() for m in modules]
    }


@router.get(
    "/module/{module_name}",
    summary="Get module details",
    description="Get details of a specific module."
)
async def get_module(module_name: str):
    """Get module details."""
    
    module = content_storage.get_module(module_name)
    
    if not module:
        raise HTTPException(status_code=404, detail=f"Module not found: {module_name}")
    
    # Get contents count
    contents = content_storage.get_contents_by_module(module_name)
    
    return {
        "success": True,
        "module": module.to_response_dict(),
        "content_count": len(contents)
    }


# ==================== Student Access ====================

@router.get(
    "/student/content/{module_name}",
    summary="Get student content",
    description="Get approved, published content for student access."
)
async def get_student_content(
    module_name: str,
    unit_name: str = None
):
    """Get content for student access (approved only)."""
    
    contents = content_storage.get_student_content(module_name, unit_name)
    
    return {
        "success": True,
        "module_name": module_name,
        "unit_name": unit_name,
        "count": len(contents),
        "contents": contents
    }



