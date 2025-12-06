"""
Semantic Similarity Evaluator for MechGAIA Benchmark

This module provides a lightweight semantic similarity evaluation approach
that can be used as a fallback or complement to LLM-based evaluation.

Uses multiple strategies:
1. Simple keyword/concept matching
2. Text embedding similarity (if transformers available)
3. Structural pattern matching (formula detection, methodology flow)
"""

import re
import logging
from typing import Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from collections import Counter

logger = logging.getLogger(__name__)


@dataclass
class SemanticSimilarityScore:
    """Result of semantic similarity evaluation."""
    score: float  # 0.0 to 1.0
    concept_coverage: float  # How many key concepts are present
    structure_similarity: float  # How similar the reasoning structure is
    keyword_overlap: float  # Overlap in important technical terms
    feedback: str
    found_concepts: Dict[str, bool]
    reference_keywords: Set[str]
    agent_keywords: Set[str]


class SemanticSimilarityEvaluator:
    """
    Evaluates reasoning using semantic similarity without requiring LLM calls.
    Useful as a fast, deterministic alternative or complement to LLM evaluation.
    """
    
    # Technical terms and concepts database
    CONCEPT_KEYWORDS = {
        # Level 1 - Stress/Strain
        "stress_concepts": {
            "bending stress", "shear stress", "tensile stress", "compressive stress",
            "stress concentration", "maximum stress", "allowable stress", "safety factor",
            "yield strength", "ultimate tensile strength", "moment of inertia"
        },
        "stress_formulas": {
            "sigma = M*c/I", "stress = force/area", "von mises", "mohr circle",
            "elastic modulus", "poisson ratio"
        },
        "stress_methods": {
            "beam theory", "mechanics of materials", "free body diagram",
            "equilibrium", "superposition", "boundary conditions"
        },
        
        # Level 2 - Shaft Design
        "shaft_concepts": {
            "torque", "power transmission", "shear stress", "torsion", "angular velocity",
            "diameter", "safety factor", "allowable stress", "critical speed"
        },
        "shaft_formulas": {
            "t = p/omega", "torque = power/speed", "shear stress = torque*r/I",
            "polar moment", "shaft diameter", "minimum diameter"
        },
        "shaft_methods": {
            "material selection", "constraint satisfaction", "strength design",
            "power transmission design", "shaft calculation"
        },
        
        # Level 3 - Plate Optimization
        "plate_concepts": {
            "stress distribution", "optimization", "plate bending", "deflection",
            "thickness", "boundary conditions", "constraint", "objective function"
        },
        "plate_formulas": {
            "deflection", "maximum stress", "plate equation", "FEA", "finite element"
        },
        "plate_methods": {
            "iterative design", "parametric study", "sensitivity analysis",
            "optimization algorithm", "design iteration"
        }
    }
    
    def __init__(self):
        """Initialize semantic evaluator."""
        self.use_embeddings = False
        self._try_load_embeddings()
    
    def _try_load_embeddings(self):
        """Try to load sentence transformers for embedding-based similarity."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.use_embeddings = True
            logger.info("Semantic evaluator using sentence embeddings")
        except ImportError:
            logger.info("Sentence transformers not available, using keyword-based similarity")
            self.use_embeddings = False
    
    def evaluate_similarity(
        self,
        agent_reasoning: str,
        reference_reasoning: str,
        task_level: int = 1,
        key_concepts: Optional[list[str]] = None
    ) -> SemanticSimilarityScore:
        """
        Evaluate semantic similarity between agent and reference reasoning.
        
        Args:
            agent_reasoning: Agent's explanation
            reference_reasoning: Reference/ground truth explanation
            task_level: Task difficulty level (1-3)
            key_concepts: Custom key concepts to look for
        
        Returns:
            SemanticSimilarityScore with detailed breakdown
        """
        
        # Extract keywords and concepts
        agent_keywords = self._extract_keywords(agent_reasoning, task_level)
        ref_keywords = self._extract_keywords(reference_reasoning, task_level)
        
        # Calculate keyword overlap
        keyword_overlap = self._calculate_keyword_overlap(
            agent_keywords, ref_keywords
        )
        
        # Analyze concept coverage
        if key_concepts is None:
            key_concepts = self._get_default_concepts(task_level)
        
        found_concepts = {}
        for concept in key_concepts:
            found = self._concept_found(concept, agent_reasoning)
            found_concepts[concept] = found
        
        concept_coverage = sum(found_concepts.values()) / len(found_concepts) if found_concepts else 0.0
        
        # Analyze structure similarity
        structure_similarity = self._calculate_structure_similarity(
            agent_reasoning, reference_reasoning
        )
        
        # Calculate embedding-based similarity if available
        embedding_similarity = 0.0
        if self.use_embeddings:
            embedding_similarity = self._calculate_embedding_similarity(
                agent_reasoning, reference_reasoning
            )
        
        # Combine scores
        # Weight: keyword (30%), concepts (30%), structure (20%), embeddings (20%)
        overall_score = (
            0.30 * keyword_overlap +
            0.30 * concept_coverage +
            0.20 * structure_similarity +
            0.20 * embedding_similarity
        )
        
        # Generate feedback
        feedback = self._generate_feedback(
            keyword_overlap, concept_coverage, structure_similarity,
            found_concepts
        )
        
        return SemanticSimilarityScore(
            score=overall_score,
            concept_coverage=concept_coverage,
            structure_similarity=structure_similarity,
            keyword_overlap=keyword_overlap,
            feedback=feedback,
            found_concepts=found_concepts,
            reference_keywords=ref_keywords,
            agent_keywords=agent_keywords
        )
    
    def _extract_keywords(self, text: str, task_level: int) -> Set[str]:
        """Extract technical keywords from text."""
        text_lower = text.lower()
        keywords = set()
        
        # Get relevant concept database for task level
        if task_level == 1:
            concept_set = (
                self.CONCEPT_KEYWORDS["stress_concepts"] |
                self.CONCEPT_KEYWORDS["stress_formulas"] |
                self.CONCEPT_KEYWORDS["stress_methods"]
            )
        elif task_level == 2:
            concept_set = (
                self.CONCEPT_KEYWORDS["shaft_concepts"] |
                self.CONCEPT_KEYWORDS["shaft_formulas"] |
                self.CONCEPT_KEYWORDS["shaft_methods"]
            )
        else:  # level 3
            concept_set = (
                self.CONCEPT_KEYWORDS["plate_concepts"] |
                self.CONCEPT_KEYWORDS["plate_formulas"] |
                self.CONCEPT_KEYWORDS["plate_methods"]
            )
        
        # Find matching keywords
        for keyword in concept_set:
            if keyword in text_lower:
                keywords.add(keyword)
        
        # Also extract mathematical symbols and operators
        math_patterns = [
            r'[πρσμνE\w]+\s*[=<>≤≥]+\s*[\w.e\-+*/()]+',  # Equations
            r'\d+\.\d+[e]?[\-+]?\d+',  # Scientific notation
            r'[∑∫∂∇∆]+',  # Calculus symbols
        ]
        
        for pattern in math_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            keywords.update(matches)
        
        return keywords
    
    def _calculate_keyword_overlap(self, agent_kw: Set[str], ref_kw: Set[str]) -> float:
        """Calculate Jaccard similarity of keywords."""
        if not agent_kw or not ref_kw:
            return 0.5 if (bool(agent_kw) == bool(ref_kw)) else 0.0
        
        intersection = len(agent_kw & ref_kw)
        union = len(agent_kw | ref_kw)
        
        return intersection / union if union > 0 else 0.0
    
    def _concept_found(self, concept: str, text: str) -> bool:
        """Check if a concept appears in the text."""
        # Direct match
        if concept.lower() in text.lower():
            return True
        
        # Partial word match (for compound concepts)
        words = concept.lower().split()
        if len(words) > 1:
            text_lower = text.lower()
            return all(word in text_lower for word in words)
        
        return False
    
    def _get_default_concepts(self, task_level: int) -> list[str]:
        """Get default concepts to check for each task level."""
        
        if task_level == 1:
            return [
                "bending stress", "moment of inertia", "neutral axis",
                "beam theory", "equilibrium", "safety factor"
            ]
        elif task_level == 2:
            return [
                "torque", "power transmission", "shear stress", "material selection",
                "safety factor", "constraint satisfaction"
            ]
        else:  # level 3
            return [
                "stress distribution", "optimization", "design iteration",
                "deflection", "boundary conditions", "parametric"
            ]
    
    def _calculate_structure_similarity(self, agent_text: str, ref_text: str) -> float:
        """
        Analyze structural similarity (organization of reasoning).
        Looks for similar logical flow and presentation order.
        """
        
        # Extract sections/paragraphs
        agent_sections = [s.strip() for s in agent_text.split('\n\n') if s.strip()]
        ref_sections = [s.strip() for s in ref_text.split('\n\n') if s.strip()]
        
        # Compare section organization
        if not agent_sections or not ref_sections:
            return 0.5
        
        # Analyze if both start with problem statement, show calculations, etc.
        agent_patterns = self._extract_structure_patterns(agent_text)
        ref_patterns = self._extract_structure_patterns(ref_text)
        
        # Count matching patterns
        matching_patterns = set(agent_patterns) & set(ref_patterns)
        total_patterns = len(set(agent_patterns) | set(ref_patterns))
        
        if total_patterns == 0:
            return 0.5
        
        return len(matching_patterns) / total_patterns
    
    def _extract_structure_patterns(self, text: str) -> list[str]:
        """Extract structural patterns from reasoning text."""
        patterns = []
        text_lower = text.lower()
        
        # Check for problem setup
        if any(x in text_lower for x in ["given", "problem", "specified", "parameter"]):
            patterns.append("problem_setup")
        
        # Check for calculations/methodology
        if any(x in text_lower for x in ["calculate", "equation", "formula", "using"]):
            patterns.append("calculation")
        
        # Check for verification/validation
        if any(x in text_lower for x in ["verify", "check", "validate", "constraint"]):
            patterns.append("verification")
        
        # Check for conclusion/result
        if any(x in text_lower for x in ["result", "therefore", "conclusion", "answer"]):
            patterns.append("conclusion")
        
        # Check for formula mentions
        if re.search(r'[σ\w]\s*=', text):
            patterns.append("has_equations")
        
        # Check for numerical values
        if re.search(r'\d+\.?\d*\s*[a-z]', text):
            patterns.append("has_numbers")
        
        return patterns
    
    def _calculate_embedding_similarity(self, agent_text: str, ref_text: str) -> float:
        """Calculate semantic similarity using embeddings."""
        try:
            agent_embedding = self.model.encode(agent_text, convert_to_tensor=True)
            ref_embedding = self.model.encode(ref_text, convert_to_tensor=True)
            
            # Cosine similarity
            from torch import nn
            similarity = nn.functional.cosine_similarity(
                agent_embedding.unsqueeze(0),
                ref_embedding.unsqueeze(0)
            ).item()
            
            return float(max(0.0, min(1.0, similarity)))
        except Exception as e:
            logger.debug(f"Embedding similarity calculation failed: {e}")
            return 0.5
    
    def _generate_feedback(
        self,
        keyword_overlap: float,
        concept_coverage: float,
        structure_similarity: float,
        found_concepts: Dict[str, bool]
    ) -> str:
        """Generate human-readable feedback."""
        
        components = []
        
        # Keyword feedback
        if keyword_overlap > 0.7:
            components.append("Strong technical terminology alignment")
        elif keyword_overlap > 0.4:
            components.append("Moderate technical terminology overlap")
        else:
            components.append("Limited technical terminology match")
        
        # Concept feedback
        found_count = sum(found_concepts.values())
        total_count = len(found_concepts)
        if found_count == total_count:
            components.append(f"All {total_count} key concepts identified")
        elif found_count > total_count / 2:
            components.append(f"{found_count}/{total_count} key concepts identified")
        else:
            components.append(f"Only {found_count}/{total_count} key concepts found")
        
        # Structure feedback
        if structure_similarity > 0.7:
            components.append("Well-structured reasoning flow")
        elif structure_similarity > 0.4:
            components.append("Reasonable reasoning structure")
        else:
            components.append("Disorganized reasoning structure")
        
        return "; ".join(components)


def get_semantic_evaluator() -> SemanticSimilarityEvaluator:
    """Factory function to get a SemanticSimilarityEvaluator instance."""
    return SemanticSimilarityEvaluator()
