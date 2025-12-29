"""
Modules Router Module

FastAPI router for student module enrollment and content access.
Provides endpoints for students to enroll in modules and view approved content.
"""

from fastapi import APIRouter, HTTPException, Form
from typing import Optional

from .content_storage import content_storage, ContentStorageError
from .models.structured_content import Enrollment


router = APIRouter(prefix="/modules", tags=["Student Modules"])


@router.post(
    "/enroll",
    summary="Enroll student in a module",
    description="Student enrolls in a module to access its approved content."
)
async def enroll_student(
    student_id: str = Form(..., description="Student user ID"),
    module_name: str = Form(..., description="Module name to enroll in")
):
    """
    Enroll a student in a module.
    
    This allows the student to access approved content for the module.
    If the student is already enrolled, returns an error.
    """
    
    if not student_id or not student_id.strip():
        raise HTTPException(status_code=400, detail="Student ID is required")
    
    if not module_name or not module_name.strip():
        raise HTTPException(status_code=400, detail="Module name is required")
    
    try:
        enrollment = content_storage.enroll_student(
            student_id=student_id.strip(),
            module_name=module_name.strip()
        )
        
        return {
            "success": True,
            "message": f"Successfully enrolled in module '{module_name}'",
            "enrollment": enrollment.to_response_dict()
        }
        
    except ContentStorageError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to enroll student: {str(e)}"
        )


@router.get(
    "/{module_name}/content",
    summary="Get approved content for a module",
    description="Returns ONLY approved structured content for the specified module."
)
async def get_module_content(module_name: str):
    """
    Get approved content for a module.
    
    This endpoint returns only content where approved = true.
    Students can use this to access learning materials for enrolled modules.
    """
    
    if not module_name or not module_name.strip():
        raise HTTPException(status_code=400, detail="Module name is required")
    
    try:
        # Get only approved content for the module
        contents = content_storage.get_contents_by_module(
            module_name=module_name.strip(),
            approved_only=True
        )
        
        return {
            "success": True,
            "module_name": module_name,
            "count": len(contents),
            "contents": [c.to_response_dict() for c in contents]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get module content: {str(e)}"
        )


