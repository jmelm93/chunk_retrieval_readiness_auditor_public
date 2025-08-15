"""Header-based chunking for natural content sections."""

import re
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from loguru import logger

from llama_index.core.schema import TextNode, Document
from llama_index.core.node_parser.interface import NodeParser


@dataclass
class HeaderSection:
    """Represents a header and its associated content."""
    level: int  # 1 for H1, 2 for H2, etc.
    text: str  # Header text
    start_pos: int  # Start position in document
    end_pos: Optional[int] = None  # End position (start of next section)
    content: str = ""  # Content under this header
    parent_idx: Optional[int] = None  # Index of parent header


class HeaderBasedChunker(NodeParser):
    """
    Chunks documents based on their natural header structure.
    
    This creates semantically meaningful chunks that respect the document's
    original organization, making evaluation feedback more actionable.
    """
    
    def __init__(
        self,
        config: Any = None,
        min_section_length: int = 50,
        max_section_length: int = 10000,
        max_header_depth: int = 4,
        include_orphan_content: bool = True,
        preserve_hierarchy: bool = True,
        **kwargs
    ):
        """
        Initialize the header-based chunker.
        
        Args:
            config: Configuration object with chunking settings
            min_section_length: Minimum characters for a valid section
            max_section_length: Maximum characters before splitting
            max_header_depth: Maximum heading level to process (1-6)
            include_orphan_content: Include content before first header
            preserve_hierarchy: Maintain parent-child relationships
        """
        # Use config values if provided
        if config and hasattr(config, 'chunking') and hasattr(config.chunking, 'header_based'):
            hb = config.chunking.header_based
            min_section_length = hb.min_section_length
            max_section_length = hb.max_section_length
            max_header_depth = hb.max_header_depth
            include_orphan_content = hb.include_orphan_content
            preserve_hierarchy = hb.preserve_hierarchy
        
        # Store as instance variables (NodeParser allows these)
        super().__init__(
            include_metadata=True,
            include_prev_next_rel=False,
            **kwargs
        )
        
        # Set attributes after super init
        self._min_section_length = min_section_length
        self._max_section_length = max_section_length
        self._max_header_depth = max_header_depth
        self._include_orphan_content = include_orphan_content
        self._preserve_hierarchy = preserve_hierarchy
        
        logger.info(f"HeaderBasedChunker initialized (depth={self._max_header_depth}, hierarchy={self._preserve_hierarchy})")
    
    def parse_headers(self, content: str) -> List[HeaderSection]:
        """
        Extract headers from markdown content.
        
        Args:
            content: Markdown content to parse
            
        Returns:
            List of HeaderSection objects with positions
        """
        headers = []
        
        # Regex for markdown headers (# H1, ## H2, etc.)
        # Also captures ATX-style headers with closing #s
        header_pattern = re.compile(r'^(#{1,6})\s+(.+?)(?:\s*#*)?$', re.MULTILINE)
        
        for match in header_pattern.finditer(content):
            level = len(match.group(1))
            if level <= self._max_header_depth:
                headers.append(HeaderSection(
                    level=level,
                    text=match.group(2).strip(),
                    start_pos=match.start(),
                    end_pos=None,
                    content=""
                ))
        
        # Also check for Setext-style headers (underlined with = or -)
        setext_h1 = re.compile(r'^(.+)\n={3,}$', re.MULTILINE)
        setext_h2 = re.compile(r'^(.+)\n-{3,}$', re.MULTILINE)
        
        for match in setext_h1.finditer(content):
            if 1 <= self._max_header_depth:
                headers.append(HeaderSection(
                    level=1,
                    text=match.group(1).strip(),
                    start_pos=match.start(),
                    end_pos=None,
                    content=""
                ))
        
        for match in setext_h2.finditer(content):
            if 2 <= self._max_header_depth:
                headers.append(HeaderSection(
                    level=2,
                    text=match.group(1).strip(),
                    start_pos=match.start(),
                    end_pos=None,
                    content=""
                ))
        
        # Sort by position
        headers.sort(key=lambda h: h.start_pos)
        
        # Set end positions and extract content
        for i, header in enumerate(headers):
            # End position is the start of the next header
            if i < len(headers) - 1:
                header.end_pos = headers[i + 1].start_pos
            else:
                header.end_pos = len(content)
            
            # Extract content between headers
            header.content = content[header.start_pos:header.end_pos]
        
        # Establish parent-child relationships if preserving hierarchy
        if self._preserve_hierarchy:
            for i, header in enumerate(headers):
                # Find parent (previous header with lower level)
                for j in range(i - 1, -1, -1):
                    if headers[j].level < header.level:
                        header.parent_idx = j
                        break
        
        return headers
    
    def create_sections(self, content: str, headers: List[HeaderSection]) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Create content sections from headers.
        
        Args:
            content: Full document content
            headers: List of parsed headers
            
        Returns:
            List of (section_text, metadata) tuples
        """
        sections = []
        
        # Handle orphan content (before first header)
        if self._include_orphan_content and headers:
            orphan_content = content[:headers[0].start_pos].strip()
            if orphan_content and len(orphan_content) >= self._min_section_length:
                sections.append((
                    orphan_content,
                    {
                        'section_type': 'introduction',
                        'heading': '[Document Introduction]',
                        'level': 0,
                        'position': 0
                    }
                ))
        elif self._include_orphan_content and not headers:
            # No headers found, treat entire content as one section
            sections.append((
                content,
                {
                    'section_type': 'content',
                    'heading': '[No Headers]',
                    'level': 0,
                    'position': 0
                }
            ))
            return sections
        
        # Process each header section
        for i, header in enumerate(headers):
            section_content = header.content.strip()
            
            # Skip if too short
            if len(section_content) < self._min_section_length:
                logger.debug(f"Skipping short section: {header.text} ({len(section_content)} chars)")
                continue
            
            # Build metadata
            metadata = {
                'section_type': 'section',
                'heading': header.text,
                'level': header.level,
                'position': i + 1,
                'heading_hierarchy': self._get_hierarchy_path(headers, i) if self._preserve_hierarchy else None
            }
            
            # Handle oversized sections
            if len(section_content) > self._max_section_length:
                # Split into smaller chunks at paragraph boundaries
                subsections = self._split_large_section(section_content, header.text)
                for j, subsection in enumerate(subsections):
                    sub_metadata = metadata.copy()
                    sub_metadata['subsection'] = j + 1
                    sub_metadata['total_subsections'] = len(subsections)
                    sections.append((subsection, sub_metadata))
            else:
                sections.append((section_content, metadata))
        
        return sections
    
    def _get_hierarchy_path(self, headers: List[HeaderSection], current_idx: int) -> List[str]:
        """
        Get the hierarchical path to a header.
        
        Args:
            headers: All headers
            current_idx: Index of current header
            
        Returns:
            List of header texts from root to current
        """
        path = []
        header = headers[current_idx]
        path.append(header.text)
        
        parent_idx = header.parent_idx
        while parent_idx is not None:
            parent = headers[parent_idx]
            path.insert(0, parent.text)
            parent_idx = parent.parent_idx
        
        return path
    
    def _split_large_section(self, content: str, header: str) -> List[str]:
        """
        Split a large section into smaller chunks at natural boundaries.
        
        Args:
            content: Section content to split
            header: Section header for context
            
        Returns:
            List of subsection texts
        """
        # Try to split at paragraph boundaries
        paragraphs = content.split('\n\n')
        
        subsections = []
        current_subsection = f"# {header}\n\n"  # Include header in each subsection
        current_length = len(current_subsection)
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Check if adding this paragraph would exceed limit
            if current_length + len(paragraph) + 2 > self._max_section_length:
                # Save current subsection if it has content
                if current_length > len(f"# {header}\n\n"):
                    subsections.append(current_subsection.strip())
                
                # Start new subsection
                current_subsection = f"# {header} (continued)\n\n{paragraph}\n\n"
                current_length = len(current_subsection)
            else:
                current_subsection += paragraph + "\n\n"
                current_length += len(paragraph) + 2
        
        # Add final subsection
        if current_length > len(f"# {header}\n\n"):
            subsections.append(current_subsection.strip())
        
        # If no good splits found, just split at max length
        if not subsections:
            subsections = [content[:self._max_section_length]]
            if len(content) > self._max_section_length:
                subsections.append(content[self._max_section_length:])
        
        return subsections
    
    def get_nodes_from_documents(
        self,
        documents: List[Document],
        show_progress: bool = False,
        **kwargs
    ) -> List[TextNode]:
        """
        Parse documents into header-based chunks.
        
        Args:
            documents: List of documents to parse
            show_progress: Whether to show progress
            
        Returns:
            List of TextNode objects
        """
        all_nodes = []
        
        for doc_idx, document in enumerate(documents):
            nodes = self._parse_document(document, doc_idx)
            all_nodes.extend(nodes)
            
            if show_progress:
                logger.info(f"Processed document {doc_idx + 1}/{len(documents)}: {len(nodes)} sections")
        
        return all_nodes
    
    def _parse_document(self, document: Document, doc_idx: int = 0) -> List[TextNode]:
        """
        Parse a single document into header-based nodes.
        
        Args:
            document: Document to parse
            doc_idx: Document index for ID generation
            
        Returns:
            List of TextNode objects
        """
        content = document.text
        
        # Parse headers
        headers = self.parse_headers(content)
        logger.debug(f"Found {len(headers)} headers in document")
        
        # Create sections
        sections = self.create_sections(content, headers)
        logger.info(f"Created {len(sections)} sections from document")
        
        # Convert to TextNodes
        nodes = []
        for i, (section_text, section_metadata) in enumerate(sections):
            # Merge document metadata with section metadata
            node_metadata = {**document.metadata, **section_metadata}
            
            # Create node
            node = TextNode(
                text=section_text,
                id_=f"doc_{doc_idx}_section_{i}",
                metadata=node_metadata
            )
            nodes.append(node)
        
        return nodes
    
    def _parse_nodes(self, nodes: List[TextNode], show_progress: bool = False) -> List[TextNode]:
        """
        Parse existing nodes (required by IngestionPipeline).
        
        This is called by IngestionPipeline when processing. If we receive Documents
        wrapped as nodes, we extract and process them. Otherwise, pass through.
        """
        # Check if these are actually documents wrapped as nodes
        all_nodes = []
        
        for node in nodes:
            # If this node contains a full document's worth of content and no chunk_index,
            # it's likely a document that needs to be chunked
            if not node.metadata.get('chunk_index') and len(node.text) > 1000:
                # Create a temporary document and process it
                temp_doc = Document(
                    text=node.text,
                    metadata=node.metadata
                )
                # Process as document
                header_nodes = self._parse_document(temp_doc)
                all_nodes.extend(header_nodes)
                logger.debug(f"Processed document node into {len(header_nodes)} header-based sections")
            else:
                # Already chunked, pass through
                all_nodes.append(node)
        
        return all_nodes if all_nodes else nodes