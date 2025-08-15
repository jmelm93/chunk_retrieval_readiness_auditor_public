"""Enhanced report generator for comprehensive chunk audit results."""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from evaluators.composite import ChunkEvaluationResult


class EnhancedReportGenerator:
    """Generate comprehensive reports from chunk evaluation results."""
    
    def __init__(self, config: Any):
        """
        Initialize the report generator.
        
        Args:
            config: Configuration object
        """
        self.config = config
    
    def generate_report(self,
                       results: List[ChunkEvaluationResult],
                       output_dir: str = "output",
                       metadata: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Generate comprehensive reports in multiple formats.
        
        Args:
            results: List of chunk evaluation results
            output_dir: Output directory for reports
            metadata: Optional metadata (source URL, timestamp, etc.)
            
        Returns:
            Dictionary with paths to generated files
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate filenames
        base_name = self._generate_base_name(metadata, timestamp)
        
        files = {}
        
        # Generate JSON report
        json_file = os.path.join(output_dir, f"{base_name}.json")
        self._generate_json_report(results, json_file, metadata)
        files['json'] = json_file
        
        # Generate Markdown report
        md_file = os.path.join(output_dir, f"{base_name}.md")
        self._generate_markdown_report(results, md_file, metadata)
        files['markdown'] = md_file
        
        # Generate summary text
        summary_file = os.path.join(output_dir, f"{base_name}_summary.txt")
        self._generate_summary_report(results, summary_file, metadata)
        files['summary'] = summary_file
        
        logger.info(f"Reports generated: {', '.join(files.keys())}")
        
        return files
    
    def _generate_base_name(self, metadata: Optional[Dict[str, Any]], timestamp: str) -> str:
        """Generate base filename."""
        if metadata and metadata.get('source_url'):
            # Extract domain from URL
            from urllib.parse import urlparse
            domain = urlparse(metadata['source_url']).netloc
            domain = domain.replace('.', '-').replace('www-', '')
            return f"audit_{domain}_{timestamp}"
        else:
            return f"audit_{timestamp}"
    
    def _generate_json_report(self,
                              results: List[ChunkEvaluationResult],
                              filepath: str,
                              metadata: Optional[Dict[str, Any]]) -> None:
        """Generate JSON report."""
        report = {
            'metadata': metadata or {},
            'summary': self._generate_summary_stats(results),
            'chunks': [self._chunk_to_dict(r) for r in results]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"JSON report saved to {filepath}")
    
    def _generate_markdown_report(self,
                                  results: List[ChunkEvaluationResult],
                                  filepath: str,
                                  metadata: Optional[Dict[str, Any]]) -> None:
        """Generate Markdown report."""
        lines = []
        
        # Header
        lines.append("# Chunk Retrieval Readiness Audit Report\n")
        
        # Metadata
        if metadata:
            lines.append("## Source Information\n")
            if metadata.get('source_url'):
                lines.append(f"- **URL**: {metadata['source_url']}")
            if metadata.get('analyzed_at'):
                lines.append(f"- **Analyzed**: {metadata['analyzed_at']}")
            lines.append("")
        
        # Summary
        lines.append("## Executive Summary\n")
        summary = self._generate_summary_stats(results)
        lines.append(f"- **Total Chunks**: {summary['total_chunks']}")
        lines.append(f"- **Average Score**: {summary['average_score']:.1f}/100")
        lines.append(f"- **Passing Chunks**: {summary['passing_chunks']}/{summary['total_chunks']} ({summary['passing_rate']:.1f}%)")
        lines.append("")
        
        # Score distribution
        lines.append("### Score Distribution\n")
        lines.append(f"- 🟢 **Well Optimized** (≥80): {summary['well_optimized']} chunks")
        lines.append(f"- 🟡 **Needs Work** (60-79): {summary['needs_work']} chunks")
        lines.append(f"- 🔴 **Poorly Optimized** (<60): {summary['poorly_optimized']} chunks")
        lines.append("")
        
        # Top issues - COMMENTED OUT per user request
        # Keeping code for potential future use
        """
        if summary['top_issues']:
            # lines.append("### Top Issues Found\n")
            # only include 'top' if we should filter
            if self.config and hasattr(self.config, 'reporting') and self.config.reporting.filter_output:
                lines.append("### Top Issues Found\n")
            else:
                lines.append("### All Issues Found\n")
            # Check if we should filter output
            filter_output = (self.config and 
                           hasattr(self.config, 'reporting') and 
                           self.config.reporting.filter_output)
            issues_to_show = summary['top_issues'][:5] if filter_output else summary['top_issues']
            for issue, count in issues_to_show:
                lines.append(f"- {issue}: {count} occurrences")
            lines.append("")
        """
        
        # Terminology section
        lines.append(self._generate_terminology_section())
        
        # Add chunk performance overview table
        lines.append("## Chunk Performance Overview\n")
        lines.append("Click any chunk heading to jump to its detailed analysis.\n")
        lines.extend(self._generate_chunk_overview_table(results))
        lines.append("")
        
        # Detailed chunk analysis
        lines.append("## Detailed Chunk Analysis\n")
        
        for i, result in enumerate(results, 1):
            # Create anchor-friendly ID for the chunk
            anchor_id = self._create_anchor_id(i, result.heading)
            lines.append(f"### Chunk {i}: {result.heading or '[No Heading]'} {{#{anchor_id}}}\n")
            
            # Score and label
            lines.append(f"**Overall Score**: {result.total_score:.1f}/100 - {result.label}\n")
            
            # Score breakdown
            lines.append("**Score Breakdown**:")
            for evaluator, score in result.scores.items():
                # Convert normalized score (0-1) to percentage (0-100)
                score_percentage = score * 100
                lines.append(f"- {self._format_evaluator_name(evaluator)}: {score_percentage:.1f}/100")
            lines.append("")
            
            # Full chunk content (showing plain text version as evaluated)
            # Convert to plain text to show what was actually evaluated
            try:
                from ..utils import convert_to_plain_text
                plain_text_content = convert_to_plain_text(result.text_preview)
            except ImportError:
                plain_text_content = result.text_preview
            
            lines.append("**Full Content**:")
            lines.append(f"```\n{plain_text_content}\n```\n")
            
            # Feedback
            if result.feedback:
                lines.append("**Evaluation Feedback**:")
                lines.append("")
                
                # Define the order of evaluators for consistent presentation
                evaluator_order = ['query_answer', 'llm_rubric', 'structure_quality', 'entity_focus']
                
                # Process evaluators in defined order
                for evaluator_key in evaluator_order:
                    if evaluator_key in result.feedback:
                        feedback = result.feedback[evaluator_key]
                        evaluator_name = self._format_evaluator_name(evaluator_key)
                        
                        # Get the weight for this evaluator from config if available
                        weight_pct = ""
                        if hasattr(self, 'config') and hasattr(self.config, 'scoring') and hasattr(self.config.scoring, 'weights'):
                            weight = getattr(self.config.scoring.weights, evaluator_key, 0.25)
                            weight_pct = f" ({int(weight * 100)}%)"
                        
                        # All evaluators now have structured multi-line feedback
                        if '\n' in feedback:
                            lines.append(f"### {evaluator_name}{weight_pct}")
                            lines.append("─" * 40)  # Visual separator
                            lines.append(feedback)
                            lines.append("")
                        else:
                            # Fallback for any single-line feedback (shouldn't happen with new format)
                            lines.append(f"### {evaluator_name}{weight_pct}")
                            lines.append("─" * 40)
                            lines.append(feedback)
                            lines.append("")
                
                # Handle any evaluators not in the standard order
                for evaluator, feedback in result.feedback.items():
                    if evaluator not in evaluator_order:
                        evaluator_name = self._format_evaluator_name(evaluator)
                        lines.append(f"### {evaluator_name}")
                        lines.append("─" * 40)
                        lines.append(feedback)
                        lines.append("")
            
            # Note: Removed misleading "consolidated" sections that were actually just from LLM rubric
            # Each evaluator now provides its own comprehensive feedback above
            
            lines.append("---\n")
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        logger.info(f"Markdown report saved to {filepath}")
    
    def _generate_summary_report(self,
                                 results: List[ChunkEvaluationResult],
                                 filepath: str,
                                 metadata: Optional[Dict[str, Any]]) -> None:
        """Generate concise summary report."""
        lines = []
        
        lines.append("CHUNK AUDIT SUMMARY")
        lines.append("=" * 50)
        
        if metadata and metadata.get('source_url'):
            lines.append(f"Source: {metadata['source_url']}")
        
        lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        summary = self._generate_summary_stats(results)
        
        lines.append("OVERALL METRICS")
        lines.append("-" * 30)
        lines.append(f"Total Chunks: {summary['total_chunks']}")
        lines.append(f"Average Score: {summary['average_score']:.1f}/100")
        lines.append(f"Passing Rate: {summary['passing_rate']:.1f}%")
        lines.append("")
        
        lines.append("SCORE DISTRIBUTION")
        lines.append("-" * 30)
        lines.append(f"Well Optimized (≥80): {summary['well_optimized']}")
        lines.append(f"Needs Work (60-79): {summary['needs_work']}")
        lines.append(f"Poorly Optimized (<60): {summary['poorly_optimized']}")
        lines.append("")
        
        if summary['top_issues']:
            lines.append("TOP ISSUES")
            lines.append("-" * 30)
            # Check if we should filter output
            filter_output = (self.config and 
                           hasattr(self.config, 'reporting') and 
                           self.config.reporting.filter_output)
            issues_to_show = summary['top_issues'][:5] if filter_output else summary['top_issues']
            for issue, count in issues_to_show:
                lines.append(f"- {issue}: {count}x")
            lines.append("")
        
        # Worst performing chunks
        # Check if we should filter output
        filter_output = (self.config and 
                       hasattr(self.config, 'reporting') and 
                       self.config.reporting.filter_output)
        chunks_to_show = sorted(results, key=lambda x: x.total_score)[:3] if filter_output else sorted(results, key=lambda x: x.total_score)
        if chunks_to_show:
            lines.append("CHUNKS NEEDING MOST ATTENTION")
            lines.append("-" * 30)
            for chunk in chunks_to_show:
                lines.append(f"- Chunk {chunk.chunk_index + 1}: {chunk.heading or '[No Heading]'} ({chunk.total_score:.1f}/100)")
                # Extract first recommendation from LLM feedback if available
                if 'llm_rubric' in chunk.feedback:
                    try:
                        import json
                        # Try to extract recommendations from the feedback
                        feedback_text = chunk.feedback['llm_rubric']
                        if '**Key Recommendations:**' in feedback_text:
                            rec_section = feedback_text.split('**Key Recommendations:**')[1]
                            # Get first recommendation (starts with "1. ")
                            if '1. ' in rec_section:
                                first_rec = rec_section.split('1. ')[1].split('\n')[0].strip()
                                lines.append(f"  Fix: {first_rec}")
                    except:
                        pass
            lines.append("")
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        logger.info(f"Summary report saved to {filepath}")
    
    def _generate_summary_stats(self, results: List[ChunkEvaluationResult]) -> Dict[str, Any]:
        """Generate summary statistics."""
        if not results:
            return {
                'total_chunks': 0,
                'average_score': 0,
                'passing_chunks': 0,
                'passing_rate': 0,
                'well_optimized': 0,
                'needs_work': 0,
                'poorly_optimized': 0,
                'top_issues': []
            }
        
        total = len(results)
        passing = sum(1 for r in results if r.passing)
        avg_score = sum(r.total_score for r in results) / total
        
        # Count by label
        well_optimized = sum(1 for r in results if r.label == "Well Optimized")
        needs_work = sum(1 for r in results if r.label == "Needs Work")
        poorly_optimized = sum(1 for r in results if r.label == "Poorly Optimized")
        
        # Aggregate issues from feedback
        issue_counts = {}
        for result in results:
            # Extract flags from LLM rubric feedback if available
            if 'llm_rubric' in result.feedback:
                feedback_text = result.feedback['llm_rubric']
                if '**Issues Detected:**' in feedback_text:
                    issues_section = feedback_text.split('**Issues Detected:**')[1]
                    # Parse bullet points for issues
                    for line in issues_section.split('\n'):
                        if line.strip().startswith('• '):
                            issue = line.strip()[2:].strip()
                            # Use the issue description as the flag
                            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'total_chunks': total,
            'average_score': avg_score,
            'passing_chunks': passing,
            'passing_rate': (passing / total * 100) if total > 0 else 0,
            'well_optimized': well_optimized,
            'needs_work': needs_work,
            'poorly_optimized': poorly_optimized,
            'top_issues': top_issues
        }
    
    def _create_anchor_id(self, chunk_num: int, heading: Optional[str]) -> str:
        """Create a URL-friendly anchor ID for a chunk."""
        import re
        if heading:
            # Remove special characters and convert to lowercase
            clean_heading = re.sub(r'[^a-zA-Z0-9\s-]', '', heading)
            clean_heading = re.sub(r'\s+', '-', clean_heading.strip()).lower()
            # Limit length
            clean_heading = clean_heading[:50]
            return f"chunk-{chunk_num}-{clean_heading}"
        else:
            return f"chunk-{chunk_num}"
    
    def _generate_chunk_overview_table(self, results: List[ChunkEvaluationResult]) -> List[str]:
        """Generate a table overview of all chunks with scores and navigation links."""
        lines = []
        
        # Table header
        lines.append("| # | Chunk Heading | Overall | Q-A | LLM | Struct | Entity | Status |")
        lines.append("|---|---------------|---------|-----|-----|--------|--------|--------|")
        
        # Table rows
        for i, result in enumerate(results, 1):
            # Create anchor link
            anchor_id = self._create_anchor_id(i, result.heading)
            heading_text = result.heading or '[No Heading]'
            # Truncate heading if too long for table
            if len(heading_text) > 40:
                heading_text = heading_text[:37] + "..."
            
            # Create linked heading
            linked_heading = f"[{heading_text}](#{anchor_id})"
            
            # Get scores (convert normalized 0-1 to percentages for display)
            overall = f"{result.total_score:.0f}"
            qa_score = f"{result.scores.get('query_answer', 0) * 100:.0f}"
            llm_score = f"{result.scores.get('llm_rubric', 0) * 100:.0f}"
            struct_score = f"{result.scores.get('structure_quality', 0) * 100:.0f}"
            entity_score = f"{result.scores.get('entity_focus', 0) * 100:.0f}"
            
            # Status indicator
            if result.total_score >= 80:
                status = "🟢 Well optimized"
            elif result.total_score >= 60:
                status = "🟡 Needs work"
            else:
                status = "🔴 Poorly optimized"
            
            # Add row
            lines.append(f"| {i} | {linked_heading} | {overall} | {qa_score} | {llm_score} | {struct_score} | {entity_score} | {status} |")
        
        return lines
    
    def _generate_terminology_section(self) -> str:
        """Generate terminology explanation section."""
        # Get weights from config
        weights = {}
        if self.config and hasattr(self.config, 'scoring') and hasattr(self.config.scoring, 'weights'):
            w = self.config.scoring.weights
            weights = {
                'query_answer': int(w.query_answer * 100),
                'entity_focus': int(w.entity_focus * 100),
                'llm_rubric': int(w.llm_rubric * 100),
                'structure_quality': int(w.structure_quality * 100)
            }
        else:
            # Fallback defaults
            weights = {
                'query_answer': 30,
                'entity_focus': 25,
                'llm_rubric': 25,
                'structure_quality': 20
            }
        
        return f"""## How to Read This Report

### Scoring Dimensions

Each chunk is evaluated across four AI-driven dimensions:

- **Query-Answer Completeness ({weights['query_answer']}%)**: How well the chunk answers potential search queries
- **Entity Focus ({weights['entity_focus']}%)**: Topic coherence and entity concentration (AI-driven analysis)
- **LLM Rubric ({weights['llm_rubric']}%)**: AI evaluation of standalone readability, focus, and structure
- **Structure Quality ({weights['structure_quality']}%)**: AI analysis of structural effectiveness and formatting

### Score Interpretation

- **80-100 (🟢 Well Optimized)**: Ready for retrieval, minimal improvements needed
- **60-79 (🟡 Needs Work)**: Moderate issues, some improvements recommended
- **0-59 (🔴 Poorly Optimized)**: Significant revision needed for effective retrieval

### Understanding the Overview Table

The table provides a quick assessment of all chunks with clickable links:

| Column | Description |
|--------|-------------|
| **#** | Chunk number in document order |
| **Chunk Heading** | Clickable link to detailed analysis |
| **Overall** | Weighted average score (0-100) |
| **Q-A** | Query-Answer completeness score |
| **LLM** | LLM Rubric quality score |
| **Struct** | Structure Quality score |
| **Entity** | Entity Focus coherence score |
| **Status** | Overall optimization level with color indicator |

### Reading Chunk Analyses

Each chunk analysis contains:

1. **Score Summary**: Overall score, status, and breakdown by evaluator
2. **Full Content**: The complete chunk text for context
3. **Four Evaluator Sections**: Detailed analysis from each dimension

#### Query-Answer Section Elements:
- **Assessment**: Overall evaluation of query-answering capability
- **Queries Evaluated**: 5 specific test queries with individual scores (0-100)
- **Summary**: Average score and chunk type classification (Overview, Definition, Example, etc.)
- **Strengths**: What the chunk does well
- **Self-Containment Issues**: Missing context with point penalties

#### LLM Rubric Section Elements:
- **Assessment**: Overall quality evaluation
- **Rubric Scores**: Four sub-scores:
  - *Standalone Clarity*: How well it reads without context
  - *Topic Focus*: Consistency and coherence of subject matter
  - *Structure Quality*: Organization and flow
  - *Content Size*: Appropriateness for chunk retrieval (100-512 tokens ideal)
- **Issues Detected**: Specific problems found
- **Key Recommendations**: Top 3 actionable improvements

#### Structure Quality Section Elements:
- **Assessment**: Overall structural effectiveness
- **Structural Analysis**: Heading quality, scanability, information density scores
- **Key Structural Elements**: Individual elements evaluated with scores:
  - Headings, lists, tables, emphasis, code blocks, etc.
  - Each scored 0-100 based on effectiveness for AI retrieval
- **Optimization Suggestions**: Specific structural improvements

#### Entity Focus Section Elements:
- **Assessment**: Overall entity coherence evaluation
- **Entity Analysis**:
  - *Primary Topic*: Main subject identified
  - *Topic Alignment*: How well entities support the topic (0-100)
  - *Concrete Entity Ratio*: Percentage of specific vs. generic entities
- **Top Entities by Relevance**: 5 most important entities with:
  - ✓ = Concrete, specific entity (good for retrieval)
  - ○ = Generic or abstract entity (less effective)
  - Relevance percentage to chunk topic
- **Missing Critical Entities**: Important entities that should be included
- **Optimization Suggestions**: How to improve entity focus
"""
    
    def _format_evaluator_name(self, name: str) -> str:
        """Format evaluator name for display."""
        name_map = {
            'query_answer': 'Query-Answer',
            'llm_rubric': 'LLM Rubric',
            'entity_focus': 'Entity Focus',
            'structure_quality': 'Structure Quality'
        }
        return name_map.get(name, name.replace('_', ' ').title())
    
    def _chunk_to_dict(self, result: ChunkEvaluationResult) -> Dict[str, Any]:
        """Convert chunk result to dictionary."""
        chunk_dict = {
            'chunk_id': result.chunk_id,
            'chunk_index': result.chunk_index,
            'heading': result.heading,
            'text_preview': result.text_preview,
            'token_count': result.token_count,
            'scores': result.scores,
            'total_score': result.total_score,
            'label': result.label,
            'passing': result.passing,
            'feedback': result.feedback,
            'entities': result.entities
        }
        
        # Extract additional data from feedback if available
        # These are stored in the evaluator feedback now
        if 'llm_rubric' in result.feedback:
            # Parse LLM rubric feedback for structured data
            try:
                import re
                feedback_text = result.feedback['llm_rubric']
                
                # Extract flags from issues section
                flags = []
                if '**Issues Detected:**' in feedback_text:
                    issues_section = feedback_text.split('**Issues Detected:**')[1].split('\n\n')[0]
                    for line in issues_section.split('\n'):
                        if line.strip().startswith('• '):
                            flags.append(line.strip()[2:].strip())
                chunk_dict['flags'] = flags
                
                # Extract recommendations
                recommendations = []
                if '**Key Recommendations:**' in feedback_text:
                    rec_section = feedback_text.split('**Key Recommendations:**')[1].split('\n\n')[0]
                    for line in rec_section.split('\n'):
                        if re.match(r'^\d+\.\s', line.strip()):
                            recommendations.append(re.sub(r'^\d+\.\s+', '', line.strip()))
                chunk_dict['recommendations'] = recommendations
            except:
                pass
        
        return chunk_dict