"""Pydantic models for Query-Answer evaluation."""

from typing import List, Optional, Literal, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict

from ..base.models import BaseEvaluationResult, FormattingOptions


class ChunkType(str, Enum):
    """Types of content chunks in RAG systems."""
    DEFINITION = "Definition"
    EXAMPLE = "Example"
    OVERVIEW = "Overview"
    DETAIL = "Detail"
    GENERAL = "General"


class QueryEvaluation(BaseModel):
    """Evaluation of how well a chunk answers a specific query."""
    
    model_config = ConfigDict(extra='forbid')
    
    query: str = Field(
        min_length=10,
        description="A likely search query this chunk might help answer as part of multi-chunk retrieval"
    )
    score: int = Field(
        ge=0, le=100,
        description="How well this chunk contributes to answering the query (0-100)"
    )
    explanation: str = Field(
        min_length=20,
        description="Brief explanation of why this score was assigned"
    )
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Ensure query is a question or search-like phrase."""
        v = v.strip()
        if not v:
            raise ValueError("Query cannot be empty")
        return v


class SelfContainmentIssue(BaseModel):
    """Details about a self-containment issue in the chunk."""
    
    model_config = ConfigDict(extra='forbid')
    
    issue_type: str = Field(
        description="Type of self-containment issue (e.g., 'vague_reference', 'dangling_pronoun')"
    )
    example_text: str = Field(
        description="Example text from the chunk showing the issue"
    )
    impact: str = Field(
        description="How this issue impacts chunk usability in retrieval"
    )


class MissingInfoExplanation(BaseModel):
    """Explanation for why a piece of information is missing and critical."""
    
    model_config = ConfigDict(extra='forbid')
    
    item: str = Field(
        min_length=5,
        description="The specific missing information item"
    )
    explanation: str = Field(
        min_length=10,
        description="Why this item is critical for this chunk's specific focus"
    )


class QueryAnswerResult(BaseEvaluationResult):
    """Complete result from Query-Answer evaluation."""
    
    model_config = ConfigDict(extra='forbid')
    
    # Core evaluation data
    query_evaluations: List[QueryEvaluation] = Field(
        min_length=3, max_length=5,
        description="3-5 evaluated queries with scores and explanations"
    )
    
    chunk_type: ChunkType = Field(
        description="Classification of the chunk's content type"
    )
    
    # Quality indicators
    average_query_score: int = Field(
        ge=0, le=100,
        description="Average score across all evaluated queries"
    )
    
    can_standalone_answer: bool = Field(
        description="Whether chunk can fully answer at least one query independently"
    )
    
    # Missing information
    missing_info: List[str] = Field(
        max_length=5,
        description="Critical information gaps for this chunk's specific focus (provide empty list [] if none)"
    )
    
    missing_info_explanations: List[MissingInfoExplanation] = Field(
        max_length=5,
        description="Explanations for why each missing item is critical (provide empty list [] if none)"
    )
    
    # Strengths and weaknesses
    strengths: List[str] = Field(
        max_length=3,
        description="Key strengths of this chunk for retrieval (provide empty list [] if none)"
    )
    
    weaknesses: List[str] = Field(
        max_length=3,
        description="Key weaknesses or areas for improvement (provide empty list [] if none)"
    )
    
    # Self-containment issues (if any)
    self_containment_issues: List[SelfContainmentIssue] = Field(
        description="Issues with unclear references or context dependencies (provide empty list [] if none)"
    )
    
    self_containment_penalty: int = Field(
        ge=0, le=15,
        description="Points deducted for self-containment issues (max 15, provide 0 if no penalty)"
    )
    
    def as_markdown(self, options: Optional[FormattingOptions] = None) -> str:
        """Generate formatted markdown feedback.
        
        Args:
            options: Formatting options for output control
            
        Returns:
            Formatted markdown string
        """
        options = options or FormattingOptions()
        lines = []
        
        # Assessment
        lines.append("**Assessment:**")
        lines.append(self.explanation)
        
        # Queries Evaluated Section
        if self.query_evaluations:
            query_count = len(self.query_evaluations)
            lines.append(f"\n**Queries Evaluated ({query_count} queries):**")
            
            # Show all queries or filtered based on options
            queries_to_show = self.query_evaluations
            if options.filter_output and len(queries_to_show) > options.max_items:
                queries_to_show = queries_to_show[:options.max_items]
            
            for eval in queries_to_show:
                lines.append(f'• "{eval.query}" → {eval.score}/100')
                if options.verbosity != "concise":
                    lines.append(f"  {eval.explanation}")
            
            # Summary Statistics
            lines.append("\n**Summary:**")
            lines.append(f"Average Query Contribution Score: {self.average_query_score}%")
            lines.append(f"Chunk Type: {self.chunk_type.value}")
        
        # Strengths (if scoring well)
        if self.strengths and self.score >= 60:
            self._add_section_if_content(
                lines, "Strengths",
                self._format_list_items(self.strengths, options)
            )
        
        # Self-Containment Issues
        if self.self_containment_issues and self.self_containment_penalty > 0:
            lines.append(f"\n**Self-Containment Issues (-{self.self_containment_penalty} points):**")
            
            issues_to_show = self.self_containment_issues
            if options.filter_output and len(issues_to_show) > 3:
                issues_to_show = issues_to_show[:3]
            
            for issue in issues_to_show:
                lines.append(f'• "{issue.example_text}" - {issue.impact}')
        
        # Critical Information Gaps
        if self.missing_info and self.missing_info[0]:
            lines.append("\n**Critical Information Gaps:**")
            
            items_to_show = self.missing_info
            if options.filter_output and len(items_to_show) > 3:
                items_to_show = items_to_show[:3]
            
            for item in items_to_show:
                lines.append(f"• {item}")
                # Find matching explanation
                for explanation in self.missing_info_explanations:
                    if explanation.item == item:
                        lines.append(f"  → {explanation.explanation}")
                        break
        
        # Areas for Improvement (if not scoring well)
        if self.weaknesses and self.score < 70:
            self._add_section_if_content(
                lines, "Areas for Improvement",
                self._format_list_items(self.weaknesses, options)
            )
        
        return "\n".join(lines)
    
    def as_json_summary(self) -> Dict[str, Any]:
        """Generate a summary JSON representation.
        
        Returns:
            Dictionary with key metrics and insights
        """
        return {
            "evaluator": self.evaluator_name,
            "score": self.score,
            "passing": self.passing,
            "chunk_type": self.chunk_type.value,
            "average_query_score": self.average_query_score,
            "can_standalone_answer": self.can_standalone_answer,
            "query_count": len(self.query_evaluations),
            "best_query": max(self.query_evaluations, key=lambda x: x.score).query if self.query_evaluations else None,
            "worst_query": min(self.query_evaluations, key=lambda x: x.score).query if self.query_evaluations else None,
            "critical_gaps": len(self.missing_info),
            "self_containment_penalty": self.self_containment_penalty
        }