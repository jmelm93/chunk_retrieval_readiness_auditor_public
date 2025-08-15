"""Enhanced document loader with Firecrawl integration."""

import os
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from loguru import logger

from llama_index.core import Document
from llama_index.readers.web import SimpleWebPageReader
from bs4 import BeautifulSoup
import markdown_it

try:
    from firecrawl import FirecrawlApp
    FIRECRAWL_AVAILABLE = True
except ImportError:
    FIRECRAWL_AVAILABLE = False
    logger.warning("Firecrawl not available. Install with: pip install firecrawl-py")

# Import ContentBoundaryAnalyzer
from extractors.content_boundary_analyzer import ContentBoundaryAnalyzer, ContentBoundaryAnalysis

class EnhancedDocumentLoader:
    """Load documents from URLs or local content with enhanced metadata."""
    
    def __init__(self, 
                 firecrawl_api_key: Optional[str] = None,
                 openai_api_key: Optional[str] = None,
                 enable_boundary_analysis: bool = True,
                 boundary_analysis_length: int = 10000,
                 boundary_min_confidence: int = 3,
                 config: Optional[Any] = None):
        """
        Initialize the document loader.
        
        Args:
            firecrawl_api_key: Optional Firecrawl API key for enhanced web scraping
            openai_api_key: Optional OpenAI API key for content boundary analysis
            enable_boundary_analysis: Whether to enable content boundary detection
            boundary_analysis_length: Characters to analyze at each end
            boundary_min_confidence: Minimum confidence to apply boundaries
            config: Optional configuration object
        """
        self.config = config
        self.firecrawl_api_key = firecrawl_api_key or os.getenv("FIRECRAWL_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.firecrawl_app = None
        self.boundary_analyzer = None
        
        # Use config values if provided, otherwise use defaults
        if config and hasattr(config, 'content_preprocessing'):
            self.enable_boundary_analysis = config.content_preprocessing.enabled
            self.boundary_analysis_length = config.content_preprocessing.analysis_length
            self.boundary_min_confidence = config.content_preprocessing.min_confidence
        else:
            self.enable_boundary_analysis = enable_boundary_analysis
            self.boundary_analysis_length = boundary_analysis_length
            self.boundary_min_confidence = boundary_min_confidence
        
        # Initialize Firecrawl if available
        if self.firecrawl_api_key and FIRECRAWL_AVAILABLE:
            try:
                self.firecrawl_app = FirecrawlApp(api_key=self.firecrawl_api_key)
                logger.info("Firecrawl initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Firecrawl: {e}")
                self.firecrawl_app = None
        else:
            if not FIRECRAWL_AVAILABLE:
                logger.warning("Firecrawl library not installed")
            else:
                logger.warning("No Firecrawl API key provided")
        
        # Initialize ContentBoundaryAnalyzer if enabled and API key available
        if self.enable_boundary_analysis and self.openai_api_key:
            try:
                # Get boundary analyzer config values
                if config and hasattr(config, 'content_preprocessing'):
                    cp = config.content_preprocessing
                    # Check for model override, otherwise use default
                    if config.models.overrides and 'content_preprocessing' in config.models.overrides:
                        model = config.models.overrides['content_preprocessing']
                    else:
                        model = config.models.default
                    
                    # Get max_concurrent from concurrency config
                    max_concurrent = config.concurrency.max_llm_calls if hasattr(config, 'concurrency') else 10
                    
                    self.boundary_analyzer = ContentBoundaryAnalyzer(
                        openai_api_key=self.openai_api_key,
                        model=model,
                        max_concurrent=max_concurrent,
                        similarity_threshold=cp.similarity_threshold,
                        min_content_size=cp.min_content_size,
                        min_truncated_size=cp.min_truncated_size
                    )
                else:
                    self.boundary_analyzer = ContentBoundaryAnalyzer(
                        openai_api_key=self.openai_api_key,
                        model="gpt-5-mini"
                    )
                logger.info("ContentBoundaryAnalyzer initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize ContentBoundaryAnalyzer: {e}")
                self.boundary_analyzer = None
        elif not self.openai_api_key:
            logger.warning("No OpenAI API key provided - content boundary analysis disabled")
        else:
            logger.info("Content boundary analysis disabled by configuration")
    
    def load_from_url(self, url: str, max_content_length: Optional[int] = None) -> Document:
        """
        Load and convert web content to LlamaIndex Document.
        
        Args:
            url: URL to scrape
            max_content_length: Maximum content length to process (uses config value if not provided)
            
        Returns:
            Document with content and metadata
        """
        # Use config value if not provided
        if max_content_length is None:
            if self.config and hasattr(self.config, 'scraping'):
                max_content_length = self.config.scraping.max_content_length
            else:
                max_content_length = 500000
        
        if self.firecrawl_app:
            try:
                # Use Firecrawl for better extraction
                formats = ['markdown', 'html']
                only_main = True
                if self.config and hasattr(self.config, 'scraping'):
                    formats = self.config.scraping.formats
                    only_main = self.config.scraping.only_main_content
                
                result = self.firecrawl_app.scrape_url(
                    url, 
                    formats=formats,
                    only_main_content=only_main,
                )
                
                
                # # print available attributes on the result object
                # print("Available attributes on the result object:")
                # for attr in dir(result):
                #     if not attr.startswith("_"):
                #         print(f" - {attr}")

                # Extract content
                markdown_content = result.markdown  
                html_content = result.html
                original_length = len(markdown_content)
                
                # Apply content boundary analysis if enabled (for URL content)
                boundary_analysis = None
                if self.boundary_analyzer and self.enable_boundary_analysis:
                    logger.info("Applying content boundary analysis...")
                    try:
                        import asyncio
                        # Run boundary analysis asynchronously
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # If we're already in an async context, create a task
                            import concurrent.futures
                            with concurrent.futures.ThreadPoolExecutor() as executor:
                                future = executor.submit(
                                    asyncio.run,
                                    self.boundary_analyzer.analyze_boundaries(
                                        markdown_content,
                                        self.boundary_analysis_length,
                                        self.boundary_min_confidence
                                    )
                                )
                                processed_content, boundary_analysis = future.result()
                        else:
                            # If not in async context, run directly
                            processed_content, boundary_analysis = asyncio.run(
                                self.boundary_analyzer.analyze_boundaries(
                                    markdown_content,
                                    self.boundary_analysis_length,
                                    self.boundary_min_confidence
                                )
                            )
                        
                        if boundary_analysis and (boundary_analysis.should_apply_start or boundary_analysis.should_apply_end):
                            chars_removed = original_length - len(processed_content)
                            # logger.info(f"Boundary analysis removed {chars_removed} chars ({chars_removed/original_length*100:.1f}%)")
                            markdown_content = processed_content
                                
                    except Exception as e:
                        logger.error(f"Content boundary analysis failed: {e}")
                        # Continue with original content if analysis fails
                
                # Truncate if needed
                if len(markdown_content) > max_content_length:
                    logger.warning(f"Content truncated from {len(markdown_content)} to {max_content_length} characters")
                    markdown_content = self._smart_truncate(markdown_content, max_content_length)
                
                # Extract metadata (result.metadata is an object, not a dict)
                metadata = result.metadata if hasattr(result, 'metadata') else None
                
                # Build metadata dict (exclude html_content to avoid metadata overflow)
                doc_metadata = {
                    'source_url': url,
                    # 'html_content': html_content,  # Removed to prevent metadata overflow
                    'title': metadata.title if metadata and hasattr(metadata, 'title') else '',
                    'description': metadata.description if metadata and hasattr(metadata, 'description') else '',
                    'og_title': metadata.ogTitle if metadata and hasattr(metadata, 'ogTitle') else '',
                    'og_description': metadata.ogDescription if metadata and hasattr(metadata, 'ogDescription') else '',
                    'keywords': metadata.keywords if metadata and hasattr(metadata, 'keywords') else '',
                    'author': metadata.author if metadata and hasattr(metadata, 'author') else '',
                    'language': metadata.language if metadata and hasattr(metadata, 'language') else '',
                    'scraped_at': datetime.now().isoformat(),
                    'scraper': 'firecrawl',
                    'content_length': len(markdown_content),
                    'original_content_length': original_length,
                    'has_html': bool(html_content)  # Just indicate if HTML was available
                }
                
                # Add boundary analysis metadata if applicable
                if boundary_analysis:
                    doc_metadata['boundary_analysis'] = {
                        'applied': boundary_analysis.should_apply_start or boundary_analysis.should_apply_end,
                        'start_boundary': boundary_analysis.start_header if boundary_analysis.should_apply_start else None,
                        'start_confidence': boundary_analysis.start_confidence,
                        'end_boundary': boundary_analysis.end_header if boundary_analysis.should_apply_end else None,
                        'end_confidence': boundary_analysis.end_confidence,
                        'chars_removed': original_length - len(markdown_content)
                    }
                
                document = Document(
                    text=markdown_content,
                    metadata=doc_metadata
                )
                
                logger.info(f"Successfully loaded {len(markdown_content)} characters from {url}")
                return document
                
            except Exception as e:
                logger.error(f"Firecrawl failed: {e}. Falling back to SimpleWebPageReader")
        
        # Fallback to SimpleWebPageReader
        try:
            reader = SimpleWebPageReader()
            docs = reader.load_data([url])
            
            if docs:
                doc = docs[0]
                original_length = len(doc.text)
                content_to_process = doc.text
                
                # Apply content boundary analysis if enabled (for URL content)
                boundary_analysis = None
                if self.boundary_analyzer and self.enable_boundary_analysis:
                    logger.info("Applying content boundary analysis...")
                    try:
                        # Run boundary analysis
                        import asyncio
                        import concurrent.futures
                        
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # If we're already in an async context
                            with concurrent.futures.ThreadPoolExecutor() as executor:
                                future = executor.submit(
                                    asyncio.run,
                                    self.boundary_analyzer.analyze_boundaries(
                                        content_to_process,
                                        self.boundary_analysis_length,
                                        self.boundary_min_confidence
                                    )
                                )
                                processed_content, boundary_analysis = future.result()
                        else:
                            # If not in async context
                            processed_content, boundary_analysis = asyncio.run(
                                self.boundary_analyzer.analyze_boundaries(
                                    content_to_process,
                                    self.boundary_analysis_length,
                                    self.boundary_min_confidence
                                )
                            )
                        
                        if boundary_analysis and (boundary_analysis.should_apply_start or boundary_analysis.should_apply_end):
                            chars_removed = original_length - len(processed_content)
                            # logger.info(f"Boundary analysis removed {chars_removed} chars ({chars_removed/original_length*100:.1f}%)")
                            content_to_process = processed_content
                            
                    except Exception as e:
                        logger.error(f"Content boundary analysis failed: {e}")
                        # Continue with original content if analysis fails
                
                # Truncate if needed
                if len(content_to_process) > max_content_length:
                    content_to_process = self._smart_truncate(content_to_process, max_content_length)
                
                # Build metadata
                doc_metadata = {
                    'source_url': url,
                    'scraped_at': datetime.now().isoformat(),
                    'scraper': 'simple_web_reader',
                    'content_length': len(content_to_process),
                    'original_content_length': original_length
                }
                
                # Preserve any existing metadata from the original doc
                if doc.metadata:
                    doc_metadata.update(doc.metadata)
                
                # Add boundary analysis metadata if applicable
                if boundary_analysis:
                    doc_metadata['boundary_analysis'] = {
                        'applied': boundary_analysis.should_apply_start or boundary_analysis.should_apply_end,
                        'start_boundary': boundary_analysis.start_header if boundary_analysis.should_apply_start else None,
                        'start_confidence': boundary_analysis.start_confidence,
                        'end_boundary': boundary_analysis.end_header if boundary_analysis.should_apply_end else None,
                        'end_confidence': boundary_analysis.end_confidence,
                        'chars_removed': original_length - len(content_to_process)
                    }
                
                # Create new Document with processed content
                new_doc = Document(
                    text=content_to_process,
                    metadata=doc_metadata
                )
                
                logger.info(f"Successfully loaded {len(content_to_process)} characters from {url}")
                return new_doc
            else:
                raise ValueError(f"No content extracted from {url}")
                
        except Exception as e:
            logger.error(f"Failed to load URL {url}: {e}")
            raise
    
    def load_from_content(self, 
                         content: str, 
                         format: str = 'html',
                         metadata: Optional[Dict[str, Any]] = None) -> Document:
        """
        Load content directly into a Document.
        
        Args:
            content: Raw content string
            format: Content format ('html', 'markdown', 'text')
            metadata: Optional metadata to attach
            
        Returns:
            Document with content and metadata
        """
        logger.info(f"Loading {format} content directly ({len(content)} characters)")
        
        # Process content based on format
        if format == 'html':
            # Parse HTML and extract text
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text and preserve some structure
            text = soup.get_text(separator='\n', strip=True)
            
            # Try to extract title
            title = ""
            if soup.title:
                title = soup.title.string
            elif soup.find('h1'):
                title = soup.find('h1').get_text(strip=True)
            
            document = Document(
                text=text,
                metadata={
                    'format': 'html',
                    # 'html_content': content,  # Removed to prevent metadata overflow
                    'has_html': True,
                    'title': title,
                    'loaded_at': datetime.now().isoformat(),
                    'content_length': len(text),
                    **(metadata or {})
                }
            )
            
        elif format == 'markdown':
            # Convert markdown to HTML for uniformity
            md = markdown_it.MarkdownIt()
            # html_content = md.render(content)  # Generated but not stored in metadata
            
            document = Document(
                text=content,
                metadata={
                    'format': 'markdown',
                    # 'html_content': html_content,  # Removed to prevent metadata overflow
                    'has_html': False,
                    'loaded_at': datetime.now().isoformat(),
                    'content_length': len(content),
                    **(metadata or {})
                }
            )
            
        else:  # Plain text
            document = Document(
                text=content,
                metadata={
                    'format': 'text',
                    'loaded_at': datetime.now().isoformat(),
                    'content_length': len(content),
                    **(metadata or {})
                }
            )
        
        logger.info(f"Document created with {len(document.text)} characters")
        return document
    
    def load_from_file(self, file_path: str) -> Document:
        """
        Load content from a local file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Document with content and metadata
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"Loading content from file: {file_path}")
        
        # Determine format from extension
        extension = path.suffix.lower()
        format_map = {
            '.html': 'html',
            '.htm': 'html',
            '.md': 'markdown',
            '.markdown': 'markdown',
            '.txt': 'text'
        }
        
        format = format_map.get(extension, 'text')
        
        # Read content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create document
        return self.load_from_content(
            content,
            format=format,
            metadata={
                'source_file': str(path.absolute()),
                'file_name': path.name,
                'file_size': path.stat().st_size
            }
        )
    
    def _smart_truncate(self, content: str, max_length: int) -> str:
        """
        Truncate content intelligently at a natural boundary.
        
        Args:
            content: Content to truncate
            max_length: Maximum length
            
        Returns:
            Truncated content
        """
        if len(content) <= max_length:
            return content
        
        # Try to find a good truncation point
        truncated = content[:max_length]
        
        # Look for the last complete paragraph
        last_paragraph = truncated.rfind('\n\n')
        if last_paragraph > max_length * 0.8:  # If we find a paragraph break in the last 20%
            return truncated[:last_paragraph]
        
        # Look for the last complete sentence
        last_sentence = max(
            truncated.rfind('. '),
            truncated.rfind('! '),
            truncated.rfind('? ')
        )
        if last_sentence > max_length * 0.8:
            return truncated[:last_sentence + 1]
        
        # Look for the last complete line
        last_line = truncated.rfind('\n')
        if last_line > max_length * 0.8:
            return truncated[:last_line]
        
        # Just truncate at max_length
        return truncated