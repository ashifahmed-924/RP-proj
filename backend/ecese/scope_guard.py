"""
Semantic Scope Guard Module

CORE LOGIC: Ensures textbook paragraphs are ONLY attached to valid
teacher-guide topics. Everything else is discarded as "out of scope".

Uses sentence-transformers for local semantic matching.
No external API calls - fully local and explainable.
"""

import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ScopeMatchResult:
    """Result of a scope matching operation."""
    paragraph: str
    matched_topic: Optional[str]
    similarity_score: float
    is_in_scope: bool
    

@dataclass
class ScopeGuardResult:
    """Complete result of scope guard processing."""
    structured_content: Dict[str, List[str]]
    in_scope_count: int
    out_of_scope_count: int
    rejected_paragraphs: List[Tuple[str, float]]  # (paragraph, best_score)
    topic_coverage: Dict[str, int]  # topic -> paragraph count
    average_similarity: float


class SemanticScopeGuard:
    """
    Semantic Scope Guard for curriculum content alignment.
    
    Uses sentence-transformers with 'all-MiniLM-L6-v2' model to:
    1. Convert topics and paragraphs to embeddings
    2. Match paragraphs to closest topic via cosine similarity
    3. Keep only paragraphs above similarity threshold
    4. Log rejected paragraphs as "out of scope"
    
    This ensures SCOPE PRESERVATION - only curriculum-aligned content passes.
    """
    
    # Default model - lightweight and effective
    DEFAULT_MODEL = 'all-MiniLM-L6-v2'
    
    # Default similarity threshold
    DEFAULT_THRESHOLD = 0.4
    
    def __init__(
        self, 
        model_name: str = DEFAULT_MODEL,
        similarity_threshold: float = DEFAULT_THRESHOLD,
        log_rejected: bool = True
    ):
        """
        Initialize the Semantic Scope Guard.
        
        Args:
            model_name: Sentence-transformer model name
            similarity_threshold: Minimum cosine similarity to keep (0-1)
            log_rejected: Whether to log rejected paragraphs
        """
        self.model_name = model_name
        self.similarity_threshold = similarity_threshold
        self.log_rejected = log_rejected
        self._model = None
        
        logger.info(f"ScopeGuard initialized with model: {model_name}, threshold: {similarity_threshold}")
    
    @property
    def model(self):
        """Lazy-load the sentence transformer model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading sentence-transformer model: {self.model_name}")
                self._model = SentenceTransformer(self.model_name)
                logger.info("Model loaded successfully")
            except ImportError:
                raise ImportError(
                    "sentence-transformers is required. "
                    "Install with: pip install sentence-transformers"
                )
        return self._model
    
    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """
        Convert texts to embeddings.
        
        Args:
            texts: List of text strings
            
        Returns:
            Numpy array of embeddings (shape: [n_texts, embedding_dim])
        """
        if not texts:
            return np.array([])
        
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True  # Pre-normalize for faster cosine similarity
        )
        
        return embeddings
    
    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Compute cosine similarity between two sets of embeddings.
        
        Since embeddings are normalized, this is just dot product.
        
        Args:
            a: First set of embeddings (n, dim)
            b: Second set of embeddings (m, dim)
            
        Returns:
            Similarity matrix (n, m)
        """
        return np.dot(a, b.T)
    
    def match_paragraphs_to_topics(
        self,
        topics: List[str],
        paragraphs: List[str]
    ) -> List[ScopeMatchResult]:
        """
        Match each paragraph to the closest topic.
        
        Args:
            topics: List of teacher guide topic strings
            paragraphs: List of textbook paragraphs
            
        Returns:
            List of ScopeMatchResult for each paragraph
        """
        if not topics or not paragraphs:
            return []
        
        logger.info(f"Matching {len(paragraphs)} paragraphs to {len(topics)} topics...")
        
        # Encode topics and paragraphs
        topic_embeddings = self.encode_texts(topics)
        paragraph_embeddings = self.encode_texts(paragraphs)
        
        # Compute similarity matrix
        similarity_matrix = self.cosine_similarity(paragraph_embeddings, topic_embeddings)
        
        results = []
        for i, paragraph in enumerate(paragraphs):
            # Find best matching topic
            similarities = similarity_matrix[i]
            best_idx = np.argmax(similarities)
            best_score = float(similarities[best_idx])
            
            # Check if above threshold
            is_in_scope = best_score >= self.similarity_threshold
            matched_topic = topics[best_idx] if is_in_scope else None
            
            results.append(ScopeMatchResult(
                paragraph=paragraph,
                matched_topic=matched_topic,
                similarity_score=best_score,
                is_in_scope=is_in_scope
            ))
            
            # Log rejected paragraphs
            if self.log_rejected and not is_in_scope:
                logger.debug(
                    f"OUT OF SCOPE (score: {best_score:.3f}): "
                    f"{paragraph[:80]}..."
                )
        
        return results
    
    def guard_content(
        self,
        topics: List[str],
        paragraphs: List[str]
    ) -> ScopeGuardResult:
        """
        Main method: Apply scope guard to content.
        
        Attaches textbook paragraphs ONLY to valid teacher-guide topics.
        Everything else is discarded as out of scope.
        
        Args:
            topics: List of teacher guide topic strings
            paragraphs: List of textbook paragraphs
            
        Returns:
            ScopeGuardResult with structured content and statistics
        """
        # Match paragraphs to topics
        match_results = self.match_paragraphs_to_topics(topics, paragraphs)
        
        # Build structured content
        structured_content: Dict[str, List[str]] = {topic: [] for topic in topics}
        rejected_paragraphs: List[Tuple[str, float]] = []
        similarities: List[float] = []
        
        for result in match_results:
            similarities.append(result.similarity_score)
            
            if result.is_in_scope and result.matched_topic:
                structured_content[result.matched_topic].append(result.paragraph)
            else:
                rejected_paragraphs.append((result.paragraph, result.similarity_score))
        
        # Calculate statistics
        in_scope_count = len(paragraphs) - len(rejected_paragraphs)
        topic_coverage = {topic: len(paras) for topic, paras in structured_content.items()}
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
        
        # Log summary
        logger.info(
            f"Scope Guard Complete: "
            f"{in_scope_count}/{len(paragraphs)} paragraphs in scope "
            f"({100 * in_scope_count / len(paragraphs):.1f}%), "
            f"avg similarity: {avg_similarity:.3f}"
        )
        
        if rejected_paragraphs:
            logger.info(f"Rejected {len(rejected_paragraphs)} paragraphs as out of scope")
        
        return ScopeGuardResult(
            structured_content=structured_content,
            in_scope_count=in_scope_count,
            out_of_scope_count=len(rejected_paragraphs),
            rejected_paragraphs=rejected_paragraphs,
            topic_coverage=topic_coverage,
            average_similarity=avg_similarity
        )
    
    def get_topic_suggestions(
        self,
        topics: List[str],
        paragraph: str,
        top_k: int = 3
    ) -> List[Tuple[str, float]]:
        """
        Get top-k topic suggestions for a single paragraph.
        
        Useful for debugging and understanding why certain
        paragraphs are matched or rejected.
        
        Args:
            topics: List of topic strings
            paragraph: Single paragraph to match
            top_k: Number of top suggestions to return
            
        Returns:
            List of (topic, similarity_score) tuples
        """
        if not topics:
            return []
        
        topic_embeddings = self.encode_texts(topics)
        paragraph_embedding = self.encode_texts([paragraph])
        
        similarities = self.cosine_similarity(paragraph_embedding, topic_embeddings)[0]
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        return [
            (topics[idx], float(similarities[idx]))
            for idx in top_indices
        ]


class ScopeGuardLite:
    """
    Lightweight version of ScopeGuard without sentence-transformers.
    
    Uses simple keyword matching as a fallback when sentence-transformers
    is not available. Less accurate but works without ML dependencies.
    """
    
    def __init__(self, similarity_threshold: float = 0.3, log_rejected: bool = True, **kwargs):
        self.similarity_threshold = similarity_threshold
        self.log_rejected = log_rejected
    
    def keyword_similarity(self, topic: str, paragraph: str) -> float:
        """Simple keyword-based similarity."""
        topic_words = set(topic.lower().split())
        para_words = set(paragraph.lower().split())
        
        if not topic_words:
            return 0.0
        
        overlap = topic_words.intersection(para_words)
        return len(overlap) / len(topic_words)
    
    def guard_content(
        self,
        topics: List[str],
        paragraphs: List[str]
    ) -> ScopeGuardResult:
        """Apply scope guard using keyword matching."""
        structured_content: Dict[str, List[str]] = {topic: [] for topic in topics}
        rejected_paragraphs: List[Tuple[str, float]] = []
        similarities: List[float] = []
        
        for paragraph in paragraphs:
            best_topic = None
            best_score = 0.0
            
            for topic in topics:
                score = self.keyword_similarity(topic, paragraph)
                if score > best_score:
                    best_score = score
                    best_topic = topic
            
            similarities.append(best_score)
            
            if best_score >= self.similarity_threshold and best_topic:
                structured_content[best_topic].append(paragraph)
            else:
                rejected_paragraphs.append((paragraph, best_score))
        
        in_scope_count = len(paragraphs) - len(rejected_paragraphs)
        topic_coverage = {topic: len(paras) for topic, paras in structured_content.items()}
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
        
        return ScopeGuardResult(
            structured_content=structured_content,
            in_scope_count=in_scope_count,
            out_of_scope_count=len(rejected_paragraphs),
            rejected_paragraphs=rejected_paragraphs,
            topic_coverage=topic_coverage,
            average_similarity=avg_similarity
        )


def create_scope_guard(use_semantic: bool = True, **kwargs) -> SemanticScopeGuard:
    """
    Factory function to create a scope guard.
    
    Args:
        use_semantic: If True, use sentence-transformers. If False, use keyword matching.
        **kwargs: Additional arguments for the scope guard
        
    Returns:
        ScopeGuard instance
    """
    if use_semantic:
        try:
            from sentence_transformers import SentenceTransformer
            return SemanticScopeGuard(**kwargs)
        except ImportError:
            logger.warning(
                "sentence-transformers not available, falling back to keyword matching"
            )
            return ScopeGuardLite(**kwargs)
    else:
        return ScopeGuardLite(**kwargs)


# Convenience function for direct use
def guard_textbook_content(
    topics: List[str],
    paragraphs: List[str],
    similarity_threshold: float = 0.4
) -> Dict[str, List[str]]:
    """
    Apply scope guard to textbook content.
    
    Args:
        topics: List of teacher guide topic strings
        paragraphs: List of textbook paragraphs
        similarity_threshold: Minimum similarity to keep (0-1)
        
    Returns:
        Dictionary mapping topics to relevant paragraphs
    """
    guard = create_scope_guard(
        use_semantic=True,
        similarity_threshold=similarity_threshold
    )
    result = guard.guard_content(topics, paragraphs)
    return result.structured_content

