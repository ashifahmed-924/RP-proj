"""
Paragraph Extractor Module

Extracts paragraph-level content (the "Flesh") from textbook PDFs.
Uses PyMuPDF for PDF parsing - NO AI involved at this stage.
"""

import fitz  # PyMuPDF
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Paragraph:
    """Represents an extracted paragraph."""
    text: str
    page_number: int
    char_count: int
    word_count: int


class ParagraphExtractor:
    """
    Extracts clean paragraphs from textbook PDFs.
    
    This extracts the "raw content" that will later be mapped
    to the curriculum skeleton via semantic matching.
    """
    
    # Minimum paragraph length (characters)
    MIN_PARAGRAPH_LENGTH = 30
    
    # Patterns to identify paragraph breaks
    PARAGRAPH_BREAK_PATTERNS = [
        r'\n\s*\n',           # Double newline
        r'\n(?=[A-Z])',       # Newline followed by capital letter
        r'(?<=[.!?])\s+(?=[A-Z])',  # Sentence end + space + capital
    ]
    
    # Patterns to filter out (headers, page numbers, etc.)
    FILTER_PATTERNS = [
        r'^\d+$',                          # Just a number (page number)
        r'^Page\s+\d+',                    # "Page X"
        r'^Chapter\s+\d+$',                # Just "Chapter X"
        r'^Unit\s+\d+$',                   # Just "Unit X"
        r'^\s*\d+\s*$',                    # Whitespace with number
        r'^[ivxlcdm]+$',                   # Roman numerals only
        r'^Table of Contents?$',           # TOC header
        r'^Index$',                        # Index header
        r'^Bibliography$',                 # Bibliography header
        r'^References$',                   # References header
        r'^©.*$',                          # Copyright notices
        r'^ISBN[\s:]+',                    # ISBN numbers
        r'^\s*Figure\s+\d+',               # Figure captions
        r'^\s*Table\s+\d+',                # Table captions
    ]
    
    def __init__(self, min_length: int = 30):
        """
        Initialize the paragraph extractor.
        
        Args:
            min_length: Minimum paragraph length in characters
        """
        self.min_length = min_length
        self.filter_patterns = [re.compile(p, re.IGNORECASE) for p in self.FILTER_PATTERNS]
    
    def extract_raw_text(self, pdf_path: str) -> List[Tuple[int, str]]:
        """
        Extract raw text from all pages of a PDF.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of (page_number, text) tuples
        """
        pages = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num, page in enumerate(doc):
                text = page.get_text("text")
                if text.strip():
                    pages.append((page_num + 1, text))
            
            doc.close()
            
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
        
        return pages
    
    def split_into_paragraphs(self, text: str) -> List[str]:
        """
        Split text into paragraphs.
        
        Args:
            text: Raw text content
            
        Returns:
            List of paragraph strings
        """
        # First, normalize whitespace but preserve paragraph breaks
        text = text.replace('\r\n', '\n')
        text = text.replace('\r', '\n')
        
        # Split on double newlines (common paragraph separator)
        paragraphs = re.split(r'\n\s*\n', text)
        
        # Further split long blocks that might contain multiple paragraphs
        refined_paragraphs = []
        for para in paragraphs:
            # If paragraph is very long, try to split on sentence boundaries
            if len(para) > 1000:
                # Split on sentence-ending punctuation followed by newline
                sub_paras = re.split(r'(?<=[.!?])\s*\n', para)
                refined_paragraphs.extend(sub_paras)
            else:
                refined_paragraphs.append(para)
        
        return refined_paragraphs
    
    def clean_paragraph(self, text: str) -> str:
        """
        Clean a paragraph text.
        
        Args:
            text: Raw paragraph text
            
        Returns:
            Cleaned paragraph text
        """
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Remove bullet points and list markers
        text = re.sub(r'^[\s]*[•●○▪▫◦‣⁃\-\*]\s*', '', text)
        text = re.sub(r'^[\s]*\d+[.)]\s*', '', text)
        text = re.sub(r'^[\s]*[a-z][.)]\s*', '', text, flags=re.IGNORECASE)
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def should_filter(self, text: str) -> bool:
        """
        Check if a paragraph should be filtered out.
        
        Args:
            text: Paragraph text
            
        Returns:
            True if should be filtered, False otherwise
        """
        # Check length
        if len(text) < self.min_length:
            return True
        
        # Check filter patterns
        for pattern in self.filter_patterns:
            if pattern.match(text):
                return True
        
        # Check if mostly non-alphabetic
        alpha_count = sum(1 for c in text if c.isalpha())
        if len(text) > 0 and alpha_count / len(text) < 0.5:
            return True
        
        return False
    
    def extract_paragraphs(self, pdf_path: str) -> List[str]:
        """
        Main method: Extract clean paragraphs from a textbook PDF.
        
        Args:
            pdf_path: Path to the textbook PDF
            
        Returns:
            List of clean paragraph strings
        """
        all_paragraphs = []
        
        # Extract raw text from all pages
        pages = self.extract_raw_text(pdf_path)
        
        for page_num, page_text in pages:
            # Split into paragraphs
            raw_paragraphs = self.split_into_paragraphs(page_text)
            
            for raw_para in raw_paragraphs:
                # Clean the paragraph
                cleaned = self.clean_paragraph(raw_para)
                
                # Filter if needed
                if not self.should_filter(cleaned):
                    all_paragraphs.append(cleaned)
        
        return all_paragraphs
    
    def extract_paragraphs_with_metadata(self, pdf_path: str) -> List[Paragraph]:
        """
        Extract paragraphs with metadata (page number, counts).
        
        Args:
            pdf_path: Path to the textbook PDF
            
        Returns:
            List of Paragraph objects with metadata
        """
        paragraphs = []
        
        # Extract raw text from all pages
        pages = self.extract_raw_text(pdf_path)
        
        for page_num, page_text in pages:
            # Split into paragraphs
            raw_paragraphs = self.split_into_paragraphs(page_text)
            
            for raw_para in raw_paragraphs:
                # Clean the paragraph
                cleaned = self.clean_paragraph(raw_para)
                
                # Filter if needed
                if not self.should_filter(cleaned):
                    paragraphs.append(Paragraph(
                        text=cleaned,
                        page_number=page_num,
                        char_count=len(cleaned),
                        word_count=len(cleaned.split())
                    ))
        
        return paragraphs
    
    def get_extraction_stats(self, paragraphs: List[str]) -> Dict:
        """
        Get statistics about extracted paragraphs.
        
        Args:
            paragraphs: List of paragraph strings
            
        Returns:
            Statistics dictionary
        """
        if not paragraphs:
            return {
                "total_paragraphs": 0,
                "total_characters": 0,
                "total_words": 0,
                "avg_paragraph_length": 0,
                "avg_word_count": 0,
                "shortest_paragraph": 0,
                "longest_paragraph": 0
            }
        
        char_counts = [len(p) for p in paragraphs]
        word_counts = [len(p.split()) for p in paragraphs]
        
        return {
            "total_paragraphs": len(paragraphs),
            "total_characters": sum(char_counts),
            "total_words": sum(word_counts),
            "avg_paragraph_length": sum(char_counts) / len(paragraphs),
            "avg_word_count": sum(word_counts) / len(paragraphs),
            "shortest_paragraph": min(char_counts),
            "longest_paragraph": max(char_counts)
        }


# Convenience function
def extract_paragraphs_from_pdf(pdf_path: str, min_length: int = 30) -> List[str]:
    """
    Extract clean paragraphs from a textbook PDF.
    
    Args:
        pdf_path: Path to the PDF file
        min_length: Minimum paragraph length in characters
        
    Returns:
        List of clean paragraph strings
    """
    extractor = ParagraphExtractor(min_length=min_length)
    return extractor.extract_paragraphs(pdf_path)





