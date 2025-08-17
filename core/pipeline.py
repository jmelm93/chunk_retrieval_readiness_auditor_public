"""Main ingestion pipeline for chunk processing."""

import os
import re
import asyncio
from typing import List, Optional, Dict, Any
from loguru import logger

from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import (
    SemanticSplitterNodeParser,
    SentenceSplitter
)
from llama_index.core.extractors import (
    TitleExtractor,
    KeywordExtractor,
    SummaryExtractor
)
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core import Document

# Import our custom extractors
# EntityMetadataExtractor removed - entity extraction now handled during evaluation
from utils.content_validator import ContentValidator
from config import Config
from .header_chunker import HeaderBasedChunker
from .filtering_parser import FilteringNodeParser

# Note: Embedding models removed - using header-based chunking strategy

class ChunkAuditorPipeline:
    """Main pipeline for document processing and chunk creation."""
    
    def __init__(self, config: Config):
        """
        Initialize the pipeline.
        
        Args:
            config: Configuration object
        """
        self.config = config
        
        # Initialize content validator if filtering is enabled
        self.content_validator = None
        if config.filtering and config.filtering.enabled:
            try:
                self.content_validator = ContentValidator(
                    model=config.filtering.model,
                    config=config
                )
                logger.info("Content filtering enabled")
            except Exception as e:
                logger.warning(f"Could not initialize content validator: {e}")
        
        # Initialize node parser (chunking strategy)
        self.node_parser = self._get_node_parser()
        
        # Initialize extractors
        self.extractors = self._get_extractors()
        
        # Build the ingestion pipeline
        self.pipeline = self._build_pipeline()
        
        logger.info(f"Pipeline initialized with {len(self.extractors)} extractors")
    
    def _get_node_parser(self):
        """Get the configured node parser for chunking."""
        strategy = self.config.chunking.strategy
        
        # First, get the base parser based on strategy
        if strategy == "header-based":
            # Use header-based chunking for natural content sections
            base_parser = HeaderBasedChunker(config=self.config)
            logger.info("Using HeaderBasedChunker for natural content sections")
            
        elif strategy == "sentence":
            # Standard sentence-based chunking
            base_parser = SentenceSplitter(
                chunk_size=self.config.chunking.chunk_size,
                chunk_overlap=self.config.chunking.chunk_overlap
            )
            logger.info("Using SentenceSplitter for chunking")
        else:
            # Default fallback
            base_parser = SentenceSplitter(
                chunk_size=self.config.chunking.chunk_size,
                chunk_overlap=self.config.chunking.chunk_overlap
            )
            logger.info("Using SentenceSplitter (fallback) for chunking")
        
        # Wrap with filtering parser if content filtering is enabled
        if self.content_validator and self.config.filtering and self.config.filtering.enabled:
            logger.info("Wrapping parser with FilteringNodeParser for early content filtering")
            return FilteringNodeParser(
                base_parser=base_parser,
                content_validator=self.content_validator,
                enabled=True
            )
        
        return base_parser
    
    def _get_extractors(self):
        """Initialize metadata extractors."""
        extractors = []
        
        # Entity extraction is now handled by Entity Focus evaluator during evaluation phase
        # This saves Google Cloud NLP API costs and provides better context-aware extraction
        
        # Title extractor
        if self.config.extraction.extract_title:
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                try:
                    from llama_index.llms.openai import OpenAI as OpenAILLM
                    llm = OpenAILLM(
                        model=self.config.models.default,
                        api_key=openai_key
                    )
                    title_extractor = TitleExtractor(
                        nodes=self.config.extraction.title_nodes,
                        llm=llm
                    )
                    extractors.append(title_extractor)
                    logger.info("Title extractor added")
                except Exception as e:
                    logger.error(f"Failed to add title extractor: {e}")
        
        # Keyword extractor
        if self.config.extraction.extract_keywords:
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                try:
                    from llama_index.llms.openai import OpenAI as OpenAILLM
                    llm = OpenAILLM(
                        model=self.config.models.default,
                        api_key=openai_key
                    )
                    keyword_extractor = KeywordExtractor(
                        keywords=self.config.extraction.max_keywords,
                        llm=llm
                    )
                    extractors.append(keyword_extractor)
                    logger.info("Keyword extractor added")
                except Exception as e:
                    logger.error(f"Failed to add keyword extractor: {e}")
        
        # Summary extractor - temporarily disabled due to TextNode compatibility issue
        # if self.config.extraction.extract_summary:
        #     openai_key = os.getenv("OPENAI_API_KEY")
        #     if openai_key:
        #         try:
        #             from llama_index.llms.openai import OpenAI as OpenAILLM
        #             llm = OpenAILLM(
        #                 model=self.config.models.default,
        #                 api_key=openai_key
        #             )
        #             summary_extractor = SummaryExtractor(
        #                 summaries=["self"],
        #                 llm=llm
        #             )
        #             extractors.append(summary_extractor)
        #             logger.info("Summary extractor added")
        #         except Exception as e:
        #             logger.error(f"Failed to add summary extractor: {e}")
        
        return extractors
    
    def _build_pipeline(self):
        """Build the ingestion pipeline."""
        # All chunking strategies use both parser and extractors
        transformations = [self.node_parser] + self.extractors
        
        # Create pipeline with caching
        # Use duplicates_only strategy since we're not using a vector store
        pipeline = IngestionPipeline(
            transformations=transformations,
            docstore=SimpleDocumentStore(),  # Enable caching
            docstore_strategy="duplicates_only"  # Avoid warning about missing vector store
        )
        
        logger.info(f"Pipeline built with {len(transformations)} transformations")
        return pipeline
    
    def _clean_duplicate_headers(self, node):
        """Remove redundant headers from node.text that match metadata heading.
        
        Fixes issue where chunk_heading metadata duplicates the first line of chunk_text,
        causing evaluators to flag normal data structure as "problematic repetition".
        
        Args:
            node: TextNode with potential header duplication
        """
        if not hasattr(node, 'metadata') or not node.metadata.get('heading'):
            return
        
        heading = node.metadata['heading'].strip()
        if not heading:
            return
            
        text_lines = node.text.split('\n')
        if not text_lines or not text_lines[0].strip():
            return
            
        first_line = text_lines[0].strip()
        
        # Remove markdown markers and normalize for comparison
        cleaned_first = re.sub(r'^#+\s*', '', first_line)
        cleaned_first = re.sub(r'\s*\([^)]+\)$', '', cleaned_first).strip()
        
        # Conservative matching - only remove if substantial similarity
        heading_lower = heading.lower()
        cleaned_lower = cleaned_first.lower()
        
        # Check for exact match or substantial overlap
        should_remove = (
            cleaned_lower == heading_lower or
            (len(cleaned_first) > 10 and 
             (cleaned_lower in heading_lower or heading_lower in cleaned_lower) and
             len(cleaned_lower) > len(heading_lower) * 0.7)  # At least 70% overlap
        )
        
        if should_remove:
            # Remove the first line and clean up whitespace
            remaining_lines = text_lines[1:]
            # Skip empty lines after header removal
            while remaining_lines and not remaining_lines[0].strip():
                remaining_lines = remaining_lines[1:]
            
            node.text = '\n'.join(remaining_lines).strip()
            logger.debug(f"Removed duplicate header from chunk: '{first_line}' -> metadata heading: '{heading}'")
    
    async def process_document(self, document: Document) -> List:
        """
        Process a document through the pipeline.
        
        Args:
            document: LlamaIndex Document to process
            
        Returns:
            List of processed nodes with metadata
        """
        logger.info(f"Processing document with {len(document.text)} characters")
        
        try:
            # Run through pipeline (filtering now happens during chunking if enabled)
            nodes = await self.pipeline.arun(documents=[document])
            
            # Apply AI-based content validation if enabled
            # Note: Quick filtering already happened in FilteringNodeParser
            # This is for deeper AI-based validation that requires API calls
            if self.content_validator and self.config.filtering and self.config.filtering.enabled:
                filtered_nodes = []
                filtered_count = 0
                
                # Only run AI validation on chunks that passed quick filters
                for node in nodes:
                    # Skip AI validation if already pre-filtered (shouldn't happen but check anyway)
                    if hasattr(node, 'metadata') and node.metadata.get('pre_filtered', False):
                        continue
                    
                    # Run AI validation (this makes API calls)
                    try:
                        validation = await self.content_validator.validate_chunk(node.text)
                        
                        if validation.should_analyze:
                            filtered_nodes.append(node)
                        else:
                            filtered_count += 1
                            if self.config.filtering.log_filtered:
                                logger.info(f"AI-filtered {validation.content_type}: {validation.reason[:50]}")
                            
                            # Optionally save filtered chunks for review
                            if self.config.filtering.save_filtered:
                                node.metadata['ai_filtered'] = True
                                node.metadata['filter_reason'] = validation.reason
                                node.metadata['content_type'] = validation.content_type
                    except Exception as e:
                        logger.error(f"AI validation failed for chunk: {e}")
                        # On error, include the chunk to be safe
                        filtered_nodes.append(node)
                
                if filtered_count > 0:
                    logger.info(f"AI-filtered {filtered_count} additional chunks, keeping {len(filtered_nodes)}")
                nodes = filtered_nodes
            
            # Add additional metadata to each node
            for i, node in enumerate(nodes):
                # Add chunk index
                node.metadata['chunk_index'] = i
                node.metadata['total_chunks'] = len(nodes)
                
                # Add token count (approximate)
                token_count = len(node.text.split()) * 1.3  # Rough approximation
                node.metadata['token_count'] = int(token_count)
                
                # Extract heading if present
                lines = node.text.split('\n')
                if lines and lines[0].strip():
                    # First non-empty line might be heading
                    potential_heading = lines[0].strip()
                    if len(potential_heading) < 100:  # Reasonable heading length
                        node.metadata['heading'] = potential_heading
                
                # Clean duplicate headers to prevent evaluator false positives
                self._clean_duplicate_headers(node)
                
            logger.info(f"Created {len(nodes)} chunks from document")
            return nodes
            
        except Exception as e:
            logger.error(f"Pipeline processing failed: {e}")
            raise
    
    def process_document_sync(self, document: Document) -> List:
        """
        Synchronous version of process_document.
        
        Args:
            document: Document to process
            
        Returns:
            List of processed nodes
        """
        import asyncio
        return asyncio.run(self.process_document(document))
    
    def clear_cache(self):
        """Clear the pipeline cache."""
        if hasattr(self.pipeline, 'docstore'):
            self.pipeline.docstore = SimpleDocumentStore()
            logger.info("Pipeline cache cleared")