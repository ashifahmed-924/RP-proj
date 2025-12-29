"""
Skeleton Extractor Module

Extracts Unit/Lesson hierarchical structure from Teacher Guide PDFs.
Uses PyMuPDF (fitz) for PDF parsing - NO AI involved.
This establishes the "Scope Authority" from the official curriculum guide.
"""

import fitz  # PyMuPDF
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import OrderedDict


@dataclass
class TextBlock:
    """Represents a text block extracted from PDF."""
    text: str
    font_size: float
    page_number: int
    block_index: int
    bbox: Tuple[float, float, float, float]  # x0, y0, x1, y1
    is_bold: bool = False


class SkeletonExtractor:
    """
    Extracts hierarchical skeleton structure from Teacher Guide PDFs.
    
    The skeleton represents the official curriculum structure:
    - Units (main sections)
    - Lessons (sub-sections under units)
    
    This uses font size analysis to identify headers:
    - Larger fonts typically indicate higher-level headers (Units)
    - Smaller but still prominent fonts indicate sub-headers (Lessons)
    """
    
    # Threshold for identifying headers (font size > this value)
    HEADER_FONT_THRESHOLD = 12.0
    
    # Patterns for identifying unit/lesson headers
    UNIT_PATTERNS = [
        r'^unit\s*[\d\.]+',
        r'^chapter\s*[\d\.]+',
        r'^module\s*[\d\.]+',
        r'^section\s*[\d\.]+',
        r'^part\s*[\d\.]+',
        r'^\d+\.\s+[A-Z]',  # "1. Introduction"
    ]
    
    LESSON_PATTERNS = [
        r'^lesson\s*[\d\.]+',
        r'^\d+\.\d+',  # "1.1", "2.3"
        r'^activity\s*[\d\.]+',
        r'^topic\s*[\d\.]+',
        r'^[\d\.]+\s+\w+',  # "1.1 Title"
    ]
    
    def __init__(self, header_threshold: float = 12.0):
        """
        Initialize the skeleton extractor.
        
        Args:
            header_threshold: Minimum font size to consider as a header
        """
        self.header_threshold = header_threshold
    
    def extract_text_blocks(self, pdf_path: str) -> List[TextBlock]:
        """
        Extract text blocks with font information from a PDF.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of TextBlock objects with text and font size info
        """
        text_blocks = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num, page in enumerate(doc):
                # Get text blocks with detailed information
                blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
                
                for block_idx, block in enumerate(blocks):
                    if block["type"] == 0:  # Text block
                        for line in block.get("lines", []):
                            for span in line.get("spans", []):
                                text = span.get("text", "").strip()
                                if text:
                                    font_size = span.get("size", 0)
                                    flags = span.get("flags", 0)
                                    is_bold = bool(flags & 2**4)  # Check bold flag
                                    
                                    text_blocks.append(TextBlock(
                                        text=text,
                                        font_size=font_size,
                                        page_number=page_num + 1,
                                        block_index=block_idx,
                                        bbox=block["bbox"],
                                        is_bold=is_bold
                                    ))
            
            doc.close()
            
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
        
        return text_blocks
    
    def identify_headers(self, text_blocks: List[TextBlock]) -> List[TextBlock]:
        """
        Identify headers based on font size threshold.
        
        Args:
            text_blocks: List of extracted text blocks
            
        Returns:
            List of TextBlock objects identified as headers
        """
        headers = []
        
        for block in text_blocks:
            # Check if font size exceeds threshold
            if block.font_size > self.header_threshold:
                # Additional validation: should have meaningful content
                text = block.text.strip()
                if len(text) > 2 and not text.isdigit():
                    headers.append(block)
        
        return headers
    
    def classify_header_level(self, text: str, font_size: float, all_sizes: List[float]) -> int:
        """
        Classify the header level (1=Unit, 2=Lesson, 3=Sub-lesson).
        
        Args:
            text: Header text
            font_size: Font size of the header
            all_sizes: List of all header font sizes for relative comparison
            
        Returns:
            Header level (1, 2, or 3)
        """
        text_lower = text.lower().strip()
        
        # Check for explicit unit patterns
        for pattern in self.UNIT_PATTERNS:
            if re.match(pattern, text_lower, re.IGNORECASE):
                return 1
        
        # Check for explicit lesson patterns
        for pattern in self.LESSON_PATTERNS:
            if re.match(pattern, text_lower, re.IGNORECASE):
                return 2
        
        # Fallback to font size based classification
        if not all_sizes:
            return 2
        
        max_size = max(all_sizes)
        min_size = min(all_sizes)
        size_range = max_size - min_size
        
        if size_range < 2:
            # All similar sizes, classify by position/content
            return 2
        
        # Relative classification
        relative_pos = (font_size - min_size) / size_range
        
        if relative_pos > 0.7:
            return 1  # Unit level
        elif relative_pos > 0.3:
            return 2  # Lesson level
        else:
            return 3  # Sub-lesson level
    
    def build_skeleton(self, headers: List[TextBlock]) -> Dict[str, List[str]]:
        """
        Build hierarchical skeleton structure from headers.
        
        Args:
            headers: List of identified header TextBlocks
            
        Returns:
            Dictionary with Units as keys and Lists of Lessons as values
            Example: {"Unit 1": ["Lesson 1.1", "Lesson 1.2"], "Unit 2": ["Lesson 2.1"]}
        """
        skeleton = OrderedDict()
        
        if not headers:
            return skeleton
        
        # Get all font sizes for relative classification
        all_sizes = [h.font_size for h in headers]
        
        # Classify each header
        classified_headers = []
        for header in headers:
            level = self.classify_header_level(header.text, header.font_size, all_sizes)
            classified_headers.append((header, level))
        
        # Build the hierarchy
        current_unit = None
        
        for header, level in classified_headers:
            text = header.text.strip()
            
            # Clean up the text
            text = self._clean_header_text(text)
            
            if not text:
                continue
            
            if level == 1:
                # This is a unit
                current_unit = text
                if current_unit not in skeleton:
                    skeleton[current_unit] = []
            elif level == 2 and current_unit is not None:
                # This is a lesson under current unit
                if text not in skeleton[current_unit]:
                    skeleton[current_unit].append(text)
            elif level == 2 and current_unit is None:
                # Lesson without a unit - create a default unit
                current_unit = "General"
                if current_unit not in skeleton:
                    skeleton[current_unit] = []
                if text not in skeleton[current_unit]:
                    skeleton[current_unit].append(text)
        
        # If no structure was built, try alternative approach
        if not skeleton:
            skeleton = self._fallback_extraction(headers)
        
        return dict(skeleton)
    
    def _clean_header_text(self, text: str) -> str:
        """Clean up header text for display."""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove trailing colons
        text = text.rstrip(':')
        
        # Limit length
        if len(text) > 100:
            text = text[:97] + "..."
        
        return text
    
    def _fallback_extraction(self, headers: List[TextBlock]) -> Dict[str, List[str]]:
        """
        Fallback extraction when pattern-based extraction fails.
        Groups headers by page or uses font size only.
        """
        skeleton = OrderedDict()
        
        if not headers:
            return skeleton
        
        # Sort by font size descending to find top-level items
        sorted_headers = sorted(headers, key=lambda x: x.font_size, reverse=True)
        
        # Use the largest font size items as units
        if len(sorted_headers) > 0:
            max_size = sorted_headers[0].font_size
            threshold = max_size * 0.9  # Within 90% of max size
            
            units = [h for h in sorted_headers if h.font_size >= threshold]
            lessons = [h for h in sorted_headers if h.font_size < threshold]
            
            for unit_header in units:
                unit_text = self._clean_header_text(unit_header.text)
                if unit_text:
                    skeleton[unit_text] = []
            
            # Assign lessons to nearest preceding unit
            if skeleton:
                unit_list = list(skeleton.keys())
                for lesson in lessons:
                    lesson_text = self._clean_header_text(lesson.text)
                    if lesson_text and unit_list:
                        # Add to last unit for simplicity
                        skeleton[unit_list[-1]].append(lesson_text)
        
        return dict(skeleton)
    
    def extract_skeleton(self, pdf_path: str) -> Dict[str, List[str]]:
        """
        Main method: Extract skeleton structure from a Teacher Guide PDF.
        
        Args:
            pdf_path: Path to the Teacher Guide PDF
            
        Returns:
            Dictionary with hierarchical structure:
            {
                "Unit 1": ["Lesson 1.1", "Lesson 1.2"],
                "Unit 2": ["Lesson 2.1"]
            }
        """
        # Step 1: Extract all text blocks with font info
        text_blocks = self.extract_text_blocks(pdf_path)
        
        # Step 2: Identify headers (font size > threshold)
        headers = self.identify_headers(text_blocks)
        
        # Step 3: Build hierarchical skeleton
        skeleton = self.build_skeleton(headers)
        
        return skeleton
    
    def get_extraction_stats(self, skeleton: Dict[str, List[str]]) -> Dict:
        """
        Get statistics about the extracted skeleton.
        
        Args:
            skeleton: The extracted skeleton structure
            
        Returns:
            Dictionary with extraction statistics
        """
        total_units = len(skeleton)
        total_lessons = sum(len(lessons) for lessons in skeleton.values())
        
        return {
            "total_units": total_units,
            "total_lessons": total_lessons,
            "units": list(skeleton.keys()),
            "avg_lessons_per_unit": total_lessons / total_units if total_units > 0 else 0
        }


# Convenience function for direct use
def extract_skeleton_from_pdf(pdf_path: str, header_threshold: float = 12.0) -> Dict[str, List[str]]:
    """
    Extract skeleton structure from a Teacher Guide PDF.
    
    Args:
        pdf_path: Path to the PDF file
        header_threshold: Minimum font size for headers (default: 12)
        
    Returns:
        Dictionary with Unit -> Lessons structure
    """
    extractor = SkeletonExtractor(header_threshold=header_threshold)
    return extractor.extract_skeleton(pdf_path)





