"""Enhanced report generator for comprehensive chunk audit results."""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

# V3: ChunkEvaluationResult no longer used - working with dict results directly
from typing import Union


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
                       results: List[Union[Dict[str, Any], Any]],
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
                              results: List[Dict[str, Any]],
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
                                  results: List[Dict[str, Any]],
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
            # V3: Get heading from chunk_metadata
            heading = result.get('chunk_metadata', {}).get('heading', '')
            anchor_id = self._create_anchor_id(i, heading)
            lines.append(f"### Chunk {i}: {heading or '[No Heading]'} {{#{anchor_id}}}\n")
            
            # Score and label
            # V3: Get composite score and calculate label
            score = result.get('composite_score', result.get('total_score', 0))
            if score >= 80:
                label = "Well Optimized"
            elif score >= 60:
                label = "Needs Work"
            else:
                label = "Poorly Optimized"
            lines.append(f"**Overall Score**: {score:.1f}/100 - {label}\n")
            
            # Score breakdown
            lines.append("**Score Breakdown**:")
            # V3: Get scores from individual_results
            individual = result.get('individual_results', {})
            for evaluator, eval_result in individual.items():
                # V3: Score is already in 0-100 scale
                score_percentage = eval_result.get('score', 0)
                lines.append(f"- {self._format_evaluator_name(evaluator)}: {score_percentage:.1f}/100")
            lines.append("")
            
            # Full chunk content (showing plain text version as evaluated)
            # Convert to plain text to show what was actually evaluated
            try:
                from ..utils import convert_to_plain_text
                # V3: Get text from chunk_metadata
                text_preview = result.get('chunk_metadata', {}).get('text_preview', '')
                plain_text_content = convert_to_plain_text(text_preview)
            except ImportError:
                text_preview = result.get('chunk_metadata', {}).get('text_preview', '')
                plain_text_content = text_preview
            
            lines.append("**Chunk Content**:")
            lines.append(f"```\n{plain_text_content}\n```\n")
            
            # Feedback
            # V3: Get feedback from individual_results
            if result.get('individual_results'):
                lines.append("**Evaluation Feedback**:")
                lines.append("")
                
                # Define the order of evaluators for consistent presentation
                evaluator_order = ['query_answer', 'llm_rubric', 'structure_quality', 'entity_focus']
                
                # Process evaluators in defined order
                for evaluator_key in evaluator_order:
                    individual = result.get('individual_results', {})
                    if evaluator_key in individual:
                        feedback = individual[evaluator_key].get('feedback', '')
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
                # V3: Extract feedback from individual results
                individual = result.get('individual_results', {})
                for evaluator, eval_result in individual.items():
                    feedback = eval_result.get('feedback', '')
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
                                 results: List[Dict[str, Any]],
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
        # V3: Use dictionary access for sorting
        chunks_to_show = sorted(results, key=lambda x: x.get('composite_score', x.get('total_score', 0)))[:3] if filter_output else sorted(results, key=lambda x: x.get('composite_score', x.get('total_score', 0)))
        if chunks_to_show:
            lines.append("CHUNKS NEEDING MOST ATTENTION")
            lines.append("-" * 30)
            for chunk in chunks_to_show:
                # V3: Access as dictionary
                chunk_index = chunk.get('chunk_metadata', {}).get('chunk_index', 0)
                heading = chunk.get('chunk_metadata', {}).get('heading', '')
                score = chunk.get('composite_score', chunk.get('total_score', 0))
                lines.append(f"- Chunk {chunk_index + 1}: {heading or '[No Heading]'} ({score:.1f}/100)")
                # Extract first recommendation from feedback if available
                individual = chunk.get('individual_results', {})
                if 'llm_rubric' in individual:
                    try:
                        import json
                        # Try to extract recommendations from the feedback
                        feedback_text = individual['llm_rubric'].get('feedback', '')
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
    
    def _generate_summary_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
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
        # V3: Access dict fields directly
        passing = sum(1 for r in results if r.get('composite_passing', r.get('passing', False)))
        avg_score = sum(r.get('composite_score', r.get('total_score', 0)) for r in results) / total
        
        # Count by label (V3 doesn't have labels, so calculate based on score)
        well_optimized = sum(1 for r in results if r.get('composite_score', r.get('total_score', 0)) >= 80)
        needs_work = sum(1 for r in results if 60 <= r.get('composite_score', r.get('total_score', 0)) < 80)
        poorly_optimized = sum(1 for r in results if r.get('composite_score', r.get('total_score', 0)) < 60)
        
        # Aggregate issues from V3 individual results
        issue_counts = {}
        for result in results:
            # V3: Extract issues from individual evaluator results
            if 'individual_results' in result:
                for eval_name, eval_result in result.get('individual_results', {}).items():
                    feedback = eval_result.get('feedback', '')
                    if '**Issues:**' in feedback:
                        issues_section = feedback.split('**Issues:**')[1].split('**')[0]
                        for line in issues_section.split('\n'):
                            line = line.strip()
                            if line.startswith('- '):
                                issue = line[2:].strip()
                                if issue:
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
    
    def _generate_chunk_overview_table(self, results: List[Dict[str, Any]]) -> List[str]:
        """Generate a table overview of all chunks with scores and navigation links."""
        lines = []
        
        # Table header
        lines.append("| # | Chunk Heading | Overall | Q-A | LLM | Struct | Entity | Status |")
        lines.append("|---|---------------|---------|-----|-----|--------|--------|--------|")
        
        # Table rows
        for i, result in enumerate(results, 1):
            # Create anchor link (V3: get heading from chunk_metadata)
            heading = result.get('chunk_metadata', {}).get('heading', '')
            anchor_id = self._create_anchor_id(i, heading)
            heading_text = heading or '[No Heading]'
            # Truncate heading if too long for table
            if len(heading_text) > 40:
                heading_text = heading_text[:37] + "..."
            
            # Create linked heading
            linked_heading = f"[{heading_text}](#{anchor_id})"
            
            # Get scores (V3: from individual_results)
            overall = f"{result.get('composite_score', result.get('total_score', 0)):.0f}"
            individual = result.get('individual_results', {})
            qa_score = f"{individual.get('query_answer', {}).get('score', 0):.0f}"
            llm_score = f"{individual.get('llm_rubric', {}).get('score', 0):.0f}"
            struct_score = f"{individual.get('structure_quality', {}).get('score', 0):.0f}"
            entity_score = f"{individual.get('entity_focus', {}).get('score', 0):.0f}"
            
            # Status indicator
            overall_val = result.get('composite_score', result.get('total_score', 0))
            if overall_val >= 80:
                status = "🟢 Well optimized"
            elif overall_val >= 60:
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
    
    def _chunk_to_dict(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Convert chunk result to dictionary (V3: already a dict)."""
        # V3 results are already dictionaries
        # Check if it's already in the right format
        if 'composite_score' in result:
            # V3 format
            return result
        
        # Legacy format - try to adapt
        chunk_dict = {
            'chunk_id': result.get('chunk_id', ''),
            'chunk_index': result.get('chunk_index', 0),
            'heading': result.get('heading', ''),
            'text_preview': result.get('text_preview', ''),
            'token_count': result.get('token_count', 0),
            'scores': result.get('scores', {}),
            'total_score': result.get('total_score', 0),
            'label': result.get('label', ''),
            'passing': result.get('passing', False),
            'feedback': result.get('feedback', {}),
            'entities': result.get('entities', [])
        }
        
        # Extract additional data from feedback if available
        # These are stored in the evaluator feedback now
        # V3: Check in individual_results
        individual = result.get('individual_results', {})
        if 'llm_rubric' in individual:
            # Parse LLM rubric feedback for structured data
            try:
                import re
                feedback_text = individual['llm_rubric'].get('feedback', '')
                
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