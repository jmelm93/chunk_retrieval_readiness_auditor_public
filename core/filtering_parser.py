"""Filtering node parser that applies quick content filters during chunking."""

import asyncio
from typing import List, Optional, Any, Sequence
from loguru import logger

from llama_index.core.schema import Document, TextNode, BaseNode
from llama_index.core.node_parser import NodeParser


class FilteringNodeParser(NodeParser):
    """Wraps any node parser with quick content filtering.
    
    This parser applies pattern-based and length-based filters immediately
    after chunking, before any expensive API calls for extraction.
    """
    
    def __init__(self, 
                 base_parser: NodeParser,
                 content_validator: Optional[Any] = None,
                 enabled: bool = True,
                 **kwargs):
        """Initialize the filtering parser.
        
        Args:
            base_parser: The underlying node parser (e.g., HeaderBasedChunker)
            content_validator: ContentValidator instance for filtering
            enabled: Whether filtering is enabled
            **kwargs: Additional arguments for NodeParser
        """
        # Initialize parent with any required fields
        super().__init__(**kwargs)
        # Store our custom attributes as private to avoid field conflicts
        self._base_parser = base_parser
        self._content_validator = content_validator
        self._filtering_enabled = enabled and content_validator is not None
        
    def _parse_nodes(self, 
                     nodes: Sequence[BaseNode],
                     show_progress: bool = False,
                     **kwargs) -> List[BaseNode]:
        """Parse nodes synchronously.
        
        This is called by LlamaIndex for synchronous parsing.
        """
        # First, let the base parser do its chunking
        parsed_nodes = self._base_parser._parse_nodes(nodes, show_progress=show_progress, **kwargs)
        
        if not self._filtering_enabled:
            return parsed_nodes
            
        # Apply quick filtering
        return self._apply_quick_filters(parsed_nodes)
    
    async def _aparse_nodes(self,
                            nodes: Sequence[BaseNode], 
                            show_progress: bool = False,
                            **kwargs) -> List[BaseNode]:
        """Parse nodes asynchronously.
        
        This is called by LlamaIndex for async parsing.
        """
        # First, let the base parser do its chunking
        if hasattr(self._base_parser, '_aparse_nodes'):
            parsed_nodes = await self._base_parser._aparse_nodes(nodes, show_progress=show_progress, **kwargs)
        else:
            # Fallback to sync version if async not available
            parsed_nodes = self._base_parser._parse_nodes(nodes, show_progress=show_progress, **kwargs)
        
        if not self._filtering_enabled:
            return parsed_nodes
            
        # Apply quick filtering
        return self._apply_quick_filters(parsed_nodes)
    
    def _apply_quick_filters(self, nodes: List[BaseNode]) -> List[BaseNode]:
        """Apply quick pattern and length-based filters to nodes.
        
        This uses only the quick, non-API-based checks from ContentValidator.
        
        Args:
            nodes: List of nodes to filter
            
        Returns:
            Filtered list of nodes
        """
        if not self._content_validator:
            return nodes
            
        filtered_nodes = []
        filtered_count = 0
        total_count = len(nodes)
        
        for node in nodes:
            # Get the text from the node
            if isinstance(node, TextNode):
                text = node.text
            elif hasattr(node, 'get_content'):
                text = node.get_content()
            else:
                # If we can't get text, keep the node to be safe
                filtered_nodes.append(node)
                continue
            
            # Apply quick content check (no API calls)
            # This checks length, word count, sentence count, and patterns
            if hasattr(self._content_validator, '_quick_content_check'):
                validation = self._content_validator._quick_content_check(text)
                
                if validation is None:
                    # Passed quick checks - keep the node
                    filtered_nodes.append(node)
                else:
                    # Failed quick checks - filter out
                    filtered_count += 1
                    if hasattr(self._content_validator, 'config') and \
                       self._content_validator.config.filtering.log_filtered:
                        logger.info(f"Pre-filtered {validation.content_type}: {validation.reason[:50]}")
                        
                    # Optionally mark the node as filtered (for debugging)
                    if hasattr(node, 'metadata'):
                        node.metadata['pre_filtered'] = True
                        node.metadata['filter_reason'] = validation.reason
                        node.metadata['content_type'] = validation.content_type
            else:
                # If quick check method doesn't exist, keep the node
                filtered_nodes.append(node)
        
        if filtered_count > 0:
            logger.info(f"Pre-filtered {filtered_count}/{total_count} chunks before extraction "
                       f"(keeping {len(filtered_nodes)} chunks)")
        
        return filtered_nodes
    
    def get_nodes_from_documents(self,
                                  documents: Sequence[Document],
                                  show_progress: bool = False,
                                  **kwargs) -> List[BaseNode]:
        """Extract nodes from documents.
        
        This is the main entry point for synchronous processing.
        """
        # Let the base parser handle document processing
        nodes = self._base_parser.get_nodes_from_documents(
            documents, show_progress=show_progress, **kwargs
        )
        
        if not self._filtering_enabled:
            return nodes
            
        # Apply quick filtering
        return self._apply_quick_filters(nodes)
    
    async def aget_nodes_from_documents(self,
                                         documents: Sequence[Document],
                                         show_progress: bool = False,
                                         **kwargs) -> List[BaseNode]:
        """Extract nodes from documents asynchronously.
        
        This is the main entry point for async processing.
        """
        # Let the base parser handle document processing
        if hasattr(self._base_parser, 'aget_nodes_from_documents'):
            nodes = await self._base_parser.aget_nodes_from_documents(
                documents, show_progress=show_progress, **kwargs
            )
        else:
            # Fallback to sync version
            nodes = self._base_parser.get_nodes_from_documents(
                documents, show_progress=show_progress, **kwargs
            )
        
        if not self._filtering_enabled:
            return nodes
            
        # Apply quick filtering
        return self._apply_quick_filters(nodes)