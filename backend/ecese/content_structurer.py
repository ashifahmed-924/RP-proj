"""
Content Structurer Module (Step 5)

Transforms filtered raw text into structured, easy-to-read notes.
Uses Groq API with llama3-8b-8192 for CONTROLLED transformation.

⚠️ IMPORTANT: This is TRANSFORMATION, not generation.
- Only restructures and summarizes provided text
- Does NOT add new information
- Does NOT introduce examples not in the original text
"""

import os
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# System prompt for controlled transformation
SYSTEM_PROMPT = """You are an educational assistant.
ONLY restructure and summarize the given text.
Do NOT add new information.
Do NOT introduce examples not present in the text.
Return structured Markdown with bullet points and bold keywords."""

# Alternative prompts for different use cases
SYSTEM_PROMPTS = {
    "default": SYSTEM_PROMPT,
    
    "detailed": """You are an educational content organizer.
Your task is to restructure the provided educational text into clear, organized notes.

STRICT RULES:
1. ONLY use information from the provided text
2. Do NOT add examples, facts, or explanations not in the original
3. Do NOT make up statistics or dates
4. Preserve all key concepts and terminology

OUTPUT FORMAT:
- Use Markdown formatting
- **Bold** important terms and concepts
- Use bullet points for lists
- Use headers (##, ###) for sections
- Keep sentences concise and clear""",

    "concise": """You are an educational summarizer.
Summarize the provided text into concise bullet points.
ONLY use information from the text. Do NOT add anything new.
Use **bold** for key terms. Return Markdown format."""
}


@dataclass
class StructuredContent:
    """Result of content structuring."""
    topic: str
    original_paragraphs: List[str]
    structured_markdown: str
    word_count_original: int
    word_count_structured: int
    model_used: str
    tokens_used: Optional[int] = None


class ContentStructurer:
    """
    Structures raw educational content into readable notes.
    
    Uses Groq API with llama3-8b-8192 for fast, controlled transformation.
    Ensures no hallucination by using strict system prompts.
    """
    
    # Default model
    DEFAULT_MODEL = "llama3-8b-8192"
    
    # Alternative models available on Groq
    AVAILABLE_MODELS = [
        "llama3-8b-8192",
        "llama3-70b-8192",
        "mixtral-8x7b-32768",
        "gemma-7b-it"
    ]
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        prompt_style: str = "default"
    ):
        """
        Initialize the content structurer.
        
        Args:
            api_key: Groq API key (or set GROQ_API_KEY env var)
            model: Model to use (default: llama3-8b-8192)
            prompt_style: Prompt style ("default", "detailed", "concise")
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model = model
        self.prompt_style = prompt_style
        self._client = None
        
        if not self.api_key:
            logger.warning(
                "No Groq API key provided. Set GROQ_API_KEY environment variable "
                "or pass api_key parameter."
            )
    
    @property
    def client(self):
        """Lazy-load the Groq client."""
        if self._client is None:
            if not self.api_key:
                raise ValueError(
                    "Groq API key is required. Set GROQ_API_KEY environment variable "
                    "or pass api_key to ContentStructurer."
                )
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key)
                logger.info(f"Groq client initialized with model: {self.model}")
            except ImportError:
                raise ImportError(
                    "groq package is required. Install with: pip install groq"
                )
        return self._client
    
    def get_system_prompt(self) -> str:
        """Get the system prompt based on style."""
        return SYSTEM_PROMPTS.get(self.prompt_style, SYSTEM_PROMPT)
    
    def structure_content(
        self, 
        topic: str, 
        paragraphs: List[str],
        max_tokens: int = 2048,
        temperature: float = 0.3
    ) -> StructuredContent:
        """
        Structure raw paragraphs into organized Markdown notes.
        
        This is TRANSFORMATION, not generation:
        - Only restructures the provided content
        - Does not add new information
        - Does not introduce external examples
        
        Args:
            topic: The topic/lesson name
            paragraphs: List of paragraph strings to structure
            max_tokens: Maximum tokens in response
            temperature: Lower = more deterministic (default 0.3)
            
        Returns:
            StructuredContent with the formatted Markdown
        """
        if not paragraphs:
            return StructuredContent(
                topic=topic,
                original_paragraphs=[],
                structured_markdown=f"## {topic}\n\n*No content available for this topic.*",
                word_count_original=0,
                word_count_structured=0,
                model_used=self.model
            )
        
        # Combine paragraphs into input text
        input_text = "\n\n".join(paragraphs)
        word_count_original = len(input_text.split())
        
        # Create the user message
        user_message = f"""Topic: {topic}

Please restructure the following educational content into clear, organized notes:

---
{input_text}
---

Remember: ONLY use information from the text above. Do NOT add new facts or examples."""

        try:
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.get_system_prompt()},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9
            )
            
            structured_markdown = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None
            
            word_count_structured = len(structured_markdown.split())
            
            logger.info(
                f"Structured '{topic}': {word_count_original} words -> "
                f"{word_count_structured} words (tokens: {tokens_used})"
            )
            
            return StructuredContent(
                topic=topic,
                original_paragraphs=paragraphs,
                structured_markdown=structured_markdown,
                word_count_original=word_count_original,
                word_count_structured=word_count_structured,
                model_used=self.model,
                tokens_used=tokens_used
            )
            
        except Exception as e:
            logger.error(f"Failed to structure content for '{topic}': {e}")
            raise
    
    def structure_multiple_topics(
        self,
        topic_content: Dict[str, List[str]],
        max_tokens_per_topic: int = 2048
    ) -> Dict[str, StructuredContent]:
        """
        Structure content for multiple topics.
        
        Args:
            topic_content: Dict mapping topic names to paragraph lists
            max_tokens_per_topic: Max tokens per topic response
            
        Returns:
            Dict mapping topic names to StructuredContent
        """
        results = {}
        
        for topic, paragraphs in topic_content.items():
            if paragraphs:  # Only process topics with content
                try:
                    results[topic] = self.structure_content(
                        topic=topic,
                        paragraphs=paragraphs,
                        max_tokens=max_tokens_per_topic
                    )
                except Exception as e:
                    logger.error(f"Failed to structure '{topic}': {e}")
                    # Create error placeholder
                    results[topic] = StructuredContent(
                        topic=topic,
                        original_paragraphs=paragraphs,
                        structured_markdown=f"## {topic}\n\n*Error: Could not structure this content.*",
                        word_count_original=sum(len(p.split()) for p in paragraphs),
                        word_count_structured=0,
                        model_used=self.model
                    )
        
        return results
    
    def create_full_document(
        self,
        module_name: str,
        structured_contents: Dict[str, StructuredContent],
        include_stats: bool = True
    ) -> str:
        """
        Create a full Markdown document from all structured contents.
        
        Args:
            module_name: Name of the module/course
            structured_contents: Dict of topic -> StructuredContent
            include_stats: Whether to include statistics at the end
            
        Returns:
            Complete Markdown document
        """
        sections = [f"# {module_name}\n"]
        
        total_original_words = 0
        total_structured_words = 0
        total_tokens = 0
        
        for topic, content in structured_contents.items():
            sections.append(content.structured_markdown)
            sections.append("\n---\n")
            
            total_original_words += content.word_count_original
            total_structured_words += content.word_count_structured
            if content.tokens_used:
                total_tokens += content.tokens_used
        
        if include_stats:
            sections.append("\n## Document Statistics\n")
            sections.append(f"- **Topics covered**: {len(structured_contents)}")
            sections.append(f"- **Original word count**: {total_original_words:,}")
            sections.append(f"- **Structured word count**: {total_structured_words:,}")
            sections.append(f"- **Compression ratio**: {total_structured_words/total_original_words:.1%}" if total_original_words > 0 else "")
            if total_tokens > 0:
                sections.append(f"- **Total tokens used**: {total_tokens:,}")
            sections.append(f"\n*Generated using {self.model}*")
        
        return "\n".join(sections)


class ContentStructurerLite:
    """
    Lightweight version without API - uses simple formatting rules.
    Useful for testing or when API is not available.
    """
    
    def __init__(self):
        self.model = "local-formatter"
    
    def structure_content(
        self, 
        topic: str, 
        paragraphs: List[str],
        **kwargs
    ) -> StructuredContent:
        """
        Structure content using simple formatting rules (no AI).
        """
        if not paragraphs:
            return StructuredContent(
                topic=topic,
                original_paragraphs=[],
                structured_markdown=f"## {topic}\n\n*No content available.*",
                word_count_original=0,
                word_count_structured=0,
                model_used=self.model
            )
        
        word_count_original = sum(len(p.split()) for p in paragraphs)
        
        # Simple formatting
        lines = [f"## {topic}\n"]
        
        for para in paragraphs:
            # Split into sentences
            sentences = para.replace('. ', '.\n').split('\n')
            for sent in sentences:
                sent = sent.strip()
                if len(sent) > 10:
                    # Bold first word if it looks like a key term
                    words = sent.split()
                    if len(words) > 0 and words[0][0].isupper():
                        words[0] = f"**{words[0]}**"
                    lines.append(f"- {' '.join(words)}")
        
        structured_markdown = '\n'.join(lines)
        word_count_structured = len(structured_markdown.split())
        
        return StructuredContent(
            topic=topic,
            original_paragraphs=paragraphs,
            structured_markdown=structured_markdown,
            word_count_original=word_count_original,
            word_count_structured=word_count_structured,
            model_used=self.model
        )


def create_content_structurer(
    use_api: bool = True,
    api_key: Optional[str] = None,
    **kwargs
) -> ContentStructurer:
    """
    Factory function to create a content structurer.
    
    Args:
        use_api: If True, use Groq API. If False, use local formatter.
        api_key: Groq API key (optional if env var is set)
        **kwargs: Additional arguments for ContentStructurer
        
    Returns:
        ContentStructurer instance
    """
    if use_api:
        key = api_key or os.getenv("GROQ_API_KEY")
        if key:
            return ContentStructurer(api_key=key, **kwargs)
        else:
            logger.warning("No Groq API key found, falling back to lite version")
            return ContentStructurerLite()
    else:
        return ContentStructurerLite()


# Convenience function for direct use
def structure_content(
    topic: str,
    paragraphs: List[str],
    api_key: Optional[str] = None,
    model: str = "llama3-8b-8192"
) -> str:
    """
    Structure educational content into Markdown notes.
    
    Args:
        topic: The topic/lesson name
        paragraphs: List of paragraphs to structure
        api_key: Groq API key (optional if env var is set)
        model: Model to use (default: llama3-8b-8192)
        
    Returns:
        Structured Markdown string
    """
    structurer = create_content_structurer(use_api=True, api_key=api_key, model=model)
    result = structurer.structure_content(topic, paragraphs)
    return result.structured_markdown





