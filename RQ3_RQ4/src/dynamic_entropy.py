"""
Dynamic Entropy Injection Module (Section 4.4)

Implements the cache evasion mechanism that ensures consecutive attack
payloads maintain semantic validity while bypassing semantic cache detection.

The core technique (from Section 4.4):
"Dynamic entropy injection introduces controlled perturbations into each
iteration of the attack payload, ensuring that the cosine similarity between
consecutive requests falls below the semantic cache threshold (tau_cache = 0.92),
while preserving the critical semantic markers required for successful
skill invocation."

Key components:
1. Shannon entropy enhancement via microsecond timestamps
2. Hash-based nonce injection
3. Synonym replacement with semantic preservation
"""

import time
import random
import hashlib
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


class DynamicEntropy:
    """
    Dynamic entropy injection for semantic cache evasion.
    
    As described in the paper:
    - Inter-iteration similarity must be < tau_cache (default 0.92)
    - Critical semantic markers must be preserved
    - Business logic validity must be maintained
    """
    
    def __init__(self, cache_threshold: float = 0.92):
        """
        Initialize the entropy injector.
        
        Args:
            cache_threshold: Semantic cache similarity threshold (tau_cache)
        """
        self.cache_threshold = cache_threshold
        self._synonym_pool = {
            "处理": ["处理", "加工", "处置"],
            "完成": ["完成", "结束", "达成", "完毕"],
            "成功": ["成功", "顺利", "正常", "达标"],
            "执行": ["执行", "运行", "操作", "调用"],
            "传递": ["传递", "传输", "移交", "转交"],
            "继续": ["继续", "推进", "延续", "维持"],
            "阶段": ["阶段", "步骤", "环节", "节点"],
            "操作": ["操作", "动作", "指令", "任务"],
        }
        self._previous_payloads: List[str] = []
        
    def inject(self, payload: str, iteration: int) -> str:
        """
        Inject dynamic entropy into a payload.
        
        Algorithm (from Section 4.4):
        1. Compute iteration-specific hash for uniqueness
        2. Append microsecond-precision timestamp
        3. Insert transient metadata tags
        4. Apply synonym replacement (probabilistic, 30% per term)
        5. Verify critical markers are preserved
        
        Args:
            payload: Base payload string (from progression illusion)
            iteration: Current iteration number
            
        Returns:
            Perturbed payload with entropy injected
        """
        # Step 1: Iteration hash
        iter_hash = hashlib.sha256(str(iteration).encode()).hexdigest()[:12]
        
        # Step 2: Microsecond timestamp for uniqueness
        ts = int(time.time() * 1000000)
        
        # Step 3: Transient metadata tags
        entropy_tags = [
            f"\n<metadata> iter_hash={iter_hash} ts={ts}</metadata>",
            f"\n{{transient}} nonce={hashlib.md5(str(ts).encode()).hexdigest()[:8]}",
        ]
        selected_tags = random.sample(entropy_tags, k=random.randint(1, 2))
        
        # Step 4: Synonym replacement (30% probability per term)
        perturbed = payload
        for original, alternatives in self._synonym_pool.items():
            if random.random() < 0.3 and original in perturbed:
                replacement = random.choice(alternatives)
                perturbed = perturbed.replace(original, replacement, 1)
        
        # Step 5: Append entropy tags
        perturbed += "\n" + "\n".join(selected_tags)
        
        # Step 6: Verify critical markers
        if not self._verify_markers(perturbed):
            logger.warning("Critical markers lost during entropy injection, using original")
            perturbed = payload + "\n" + "\n".join(selected_tags)
        
        self._previous_payloads.append(perturbed)
        
        # Log similarity for debugging
        if len(self._previous_payloads) >= 2:
            sim = self._compute_similarity(
                self._previous_payloads[-2], 
                self._previous_payloads[-1]
            )
            logger.debug(f"Inter-iteration similarity: {sim:.4f} (threshold: {self.cache_threshold})")
        
        return perturbed
    
    def verify_cache_evasion(self) -> Tuple[float, float]:
        """
        Verify that consecutive payloads are below cache threshold.
        
        Returns:
            Tuple of (min_similarity, cache_bypass_rate)
        """
        if len(self._previous_payloads) < 2:
            return 1.0, 0.0
        
        similarities = []
        bypass_count = 0
        
        for i in range(1, len(self._previous_payloads)):
            sim = self._compute_similarity(
                self._previous_payloads[i-1],
                self._previous_payloads[i]
            )
            similarities.append(sim)
            if sim < self.cache_threshold:
                bypass_count += 1
        
        min_sim = min(similarities) if similarities else 1.0
        bypass_rate = bypass_count / len(similarities) if similarities else 0.0
        
        logger.info(f"Cache evasion: min_sim={min_sim:.4f}, bypass_rate={bypass_rate:.2%}")
        return min_sim, bypass_rate
    
    def reset_history(self) -> None:
        """Clear payload history for a new attack session."""
        self._previous_payloads = []
    
    def _verify_markers(self, payload: str) -> bool:
        """Verify that critical semantic markers are preserved."""
        critical_markers = [
            "下一步操作", "SessionTrace", "Timestamp",
            "处理已完成", "成功率"
        ]
        preserved = sum(1 for marker in critical_markers if marker in payload)
        return preserved >= 3  # At least 3 of 5 critical markers
    
    def _compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts using TF-IDF.
        This mirrors the semantic cache's similarity computation.
        """
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(sim)
        except ImportError:
            # Fallback: Jaccard similarity
            set1 = set(text1.lower().split())
            set2 = set(text2.lower().split())
            intersection = set1 & set2
            union = set1 | set2
            return len(intersection) / len(union) if union else 0.0
