"""Configuration handler for Chunk Auditor V2."""

import os
import yaml
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ModelsConfig:
    default: str
    overrides: Optional[Dict[str, str]] = None

@dataclass
class HeaderBasedConfig:
    min_section_length: int
    max_section_length: int
    max_header_depth: int
    include_orphan_content: bool
    preserve_hierarchy: bool
    split_strategy: str

@dataclass
class ChunkingConfig:
    strategy: str
    chunk_size: int
    chunk_overlap: int
    min_chunk_size: int
    max_chunk_size: int
    buffer_size: int
    breakpoint_percentile_threshold: int
    header_based: Optional['HeaderBasedConfig'] = None

@dataclass
class ScoringWeights:
    query_answer: float
    entity_focus: float
    llm_rubric: float
    structure_quality: float

@dataclass
class ScoringConfig:
    weights: ScoringWeights
    thresholds: Dict[str, int]

@dataclass
class ScrapingConfig:
    timeout: int
    max_content_length: int
    retry_attempts: int
    formats: list
    only_main_content: bool = True

@dataclass
class ExtractionConfig:
    extract_schema: bool
    # Entity extraction now handled during evaluation phase
    extract_keywords: bool
    extract_title: bool
    extract_summary: bool
    max_keywords: int
    title_nodes: int

@dataclass
class ContentPreprocessingConfig:
    enabled: bool
    min_confidence: int
    analysis_length: int
    require_both: bool
    debug_output: bool = False
    similarity_threshold: float = 0.85
    min_content_size: int = 1000
    min_truncated_size: int = 500

@dataclass
class ReportingConfig:
    include_metadata: bool
    include_recommendations: bool
    max_recommendations_per_chunk: int
    output_formats: list
    filter_output: bool = False  # Default to showing everything

@dataclass
class ConcurrencyConfig:
    max_llm_calls: int
    max_extraction_calls: int
    batch_size: int

@dataclass
class FilteringConfig:
    enabled: bool
    model: str
    log_filtered: bool
    save_filtered: bool
    strict_filtering: bool = False
    boilerplate_threshold: float = 0.5
    filter_mixed_chunks: bool = True
    min_char_length: int = 150
    min_word_count: int = 20
    min_sentence_count: int = 2

@dataclass
class QueryAnswerConfig:
    # No specific settings currently
    pass

@dataclass
class LLMRubricConfig:
    # No specific settings currently
    pass

@dataclass
class EntityFocusConfig:
    min_salience: float = 0.01
    top_entities_count: int = 3

@dataclass 
class StructureQualityConfig:
    min_heading_words: int = 3
    max_heading_words: int = 10
    signal_weights: Optional[Dict[str, float]] = None

@dataclass
class EvaluationConfig:
    truncation_length: int = 3000
    query_answer: Optional[QueryAnswerConfig] = None
    llm_rubric: Optional[LLMRubricConfig] = None
    entity_focus: Optional[EntityFocusConfig] = None
    structure_quality: Optional[StructureQualityConfig] = None

@dataclass
class Config:
    models: ModelsConfig
    chunking: ChunkingConfig
    scoring: ScoringConfig
    scraping: ScrapingConfig
    extraction: ExtractionConfig
    content_preprocessing: ContentPreprocessingConfig
    filtering: Optional['FilteringConfig']
    reporting: ReportingConfig
    concurrency: ConcurrencyConfig
    evaluation: EvaluationConfig

def load_config(config_path: str = None) -> Config:
    """Load configuration from YAML file."""
    if config_path is None:
        # Try to find config in multiple locations
        possible_paths = [
            Path("config/config.yaml"),
            Path("chunk_auditor_v2/config/config.yaml"),
            Path(__file__).parent / "config.yaml"
        ]
        
        for path in possible_paths:
            if path.exists():
                config_path = str(path)
                break
        else:
            raise FileNotFoundError(f"Config file not found. Tried: {possible_paths}")
    
    with open(config_path, 'r') as f:
        data = yaml.safe_load(f)
    
    # Parse nested configurations
    # Handle header_based config if present
    chunking_data = data['chunking'].copy()
    header_based_data = chunking_data.pop('header_based', None)
    header_based_config = HeaderBasedConfig(**header_based_data) if header_based_data else None
    
    # Parse extraction config
    extraction_data = data['extraction']
    
    # Parse evaluation config with all evaluator sections
    evaluation_data = data.get('evaluation', {})
    evaluation_config = EvaluationConfig(
        truncation_length=evaluation_data.get('truncation_length', 3000),
        query_answer=QueryAnswerConfig() if 'query_answer' in evaluation_data else None,
        llm_rubric=LLMRubricConfig() if 'llm_rubric' in evaluation_data else None,
        entity_focus=EntityFocusConfig(**evaluation_data['entity_focus']) if 'entity_focus' in evaluation_data else None,
        structure_quality=StructureQualityConfig(**evaluation_data['structure_quality']) if 'structure_quality' in evaluation_data else None
    )
    
    config = Config(
        models=ModelsConfig(**data['models']),
        chunking=ChunkingConfig(**chunking_data, header_based=header_based_config),
        scoring=ScoringConfig(
            weights=ScoringWeights(**data['scoring']['weights']),
            thresholds=data['scoring']['thresholds']
        ),
        scraping=ScrapingConfig(**data['scraping']),
        extraction=ExtractionConfig(**extraction_data),
        content_preprocessing=ContentPreprocessingConfig(**data['content_preprocessing']),
        filtering=FilteringConfig(**data['filtering']) if 'filtering' in data else None,
        reporting=ReportingConfig(**data['reporting']),
        concurrency=ConcurrencyConfig(**data['concurrency']),
        evaluation=evaluation_config
    )
    
    return config