"""Content boundary analyzer for identifying main content boundaries in web pages."""

import openai
import asyncio
import re
from typing import Optional, Tuple
from dataclasses import dataclass
from pydantic import BaseModel
from loguru import logger

class ContentBoundaryResult(BaseModel):
    """Result from boundary analysis."""
    header: Optional[str] = None
    confidence: int  # 1-5
    reasoning: str
    should_apply: bool

@dataclass
class ContentBoundaryAnalysis:
    """Complete boundary analysis results."""
    start_header: Optional[str]
    end_header: Optional[str] 
    start_confidence: int  # 1-5
    end_confidence: int    # 1-5
    start_reasoning: str
    end_reasoning: str
    should_apply_start: bool
    should_apply_end: bool

class ContentBoundaryAnalyzer:
    """Analyze content to find main article boundaries."""
    
    def __init__(self, openai_api_key: str, model: str = "gpt-5-mini", max_concurrent: int = 10, 
                 similarity_threshold: float = 0.85, min_content_size: int = 1000, 
                 min_truncated_size: int = 500):
        """
        Initialize the analyzer.
        
        Args:
            openai_api_key: OpenAI API key
            model: Model to use for analysis
            max_concurrent: Max concurrent API calls
            similarity_threshold: Threshold for fuzzy matching
            min_content_size: Min content size to process
            min_truncated_size: Min size after truncation
        """
        self.model = model
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.async_client = openai.AsyncOpenAI(api_key=openai_api_key)
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.similarity_threshold = similarity_threshold
        self.min_content_size = min_content_size
        self.min_truncated_size = min_truncated_size
        
        # System message for start boundary analysis
        self.start_system_message = """You are a content boundary detector. Your job is to identify where the main article content begins in a web page by finding the first meaningful content header.

Look for the first header that indicates actual article content, not:
- Navigation menus
- Breadcrumbs  
- Site headers
- Form labels
- Author bylines
- Publication dates
- Category tags

Return strict JSON with ONLY the header text (no markdown formatting like # or ##), your confidence level (1-5), and brief reasoning.

For example, if you see "# Article Title", return "Article Title" not "# Article Title".

If no clear boundary exists or content looks good from the start, return should_apply: false."""

        # System message for end boundary analysis
        self.end_system_message = """You are a content boundary detector. Your job is to identify where the main article content ends in a web page by finding the last meaningful content header.

Look for the last header that contains actual article content, before sections like:
- Related articles
- Newsletter signups
- Comments
- Footer navigation
- Social media widgets
- Author bios (if not part of main content)
- Advertisement sections

Return strict JSON with ONLY the header text (no markdown formatting like # or ##), your confidence level (1-5), and brief reasoning.

For example, if you see "## Final Thoughts", return "Final Thoughts" not "## Final Thoughts".

If no clear boundary exists or content looks good to the end, return should_apply: false."""

    async def _analyze_start_boundary(self, content_start: str) -> dict:
        """Analyze the beginning of content to find where main content starts."""
        async with self.semaphore:
            try:
                # Prepare user message for LLM
                user_message = f"""# Instruction
Analyze the beginning of this web page content and identify the first header where meaningful article content begins.

# Content Start (first {len(content_start)} characters)
{content_start}"""

                response = await self.async_client.chat.completions.parse(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.start_system_message},
                        {"role": "user", "content": user_message}
                    ],
                    response_format=ContentBoundaryResult
                )
                
                result = response.choices[0].message.parsed
                return {
                    "header": result.header,
                    "confidence": result.confidence,
                    "reasoning": result.reasoning,
                    "should_apply": result.should_apply
                }
                
            except Exception as e:
                logger.warning(f"Start boundary analysis failed: {e}")
                return {"header": None, "confidence": 1, "reasoning": f"Analysis error: {e}", "should_apply": False}

    async def _analyze_end_boundary(self, content_end: str) -> dict:
        """Analyze the end of content to find where main content ends."""
        async with self.semaphore:
            try:
                user_message = f"""# Instruction
Analyze the end of this web page content and identify the last header where meaningful article content ends.

# Content End (last {len(content_end)} characters)
{content_end}"""

                response = await self.async_client.chat.completions.parse(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.end_system_message},
                        {"role": "user", "content": user_message}
                    ],
                    response_format=ContentBoundaryResult
                )
                
                result = response.choices[0].message.parsed
                return {
                    "header": result.header,
                    "confidence": result.confidence,
                    "reasoning": result.reasoning,
                    "should_apply": result.should_apply
                }
                
            except Exception as e:
                logger.warning(f"End boundary analysis failed: {e}")
                return {"header": None, "confidence": 1, "reasoning": f"Analysis error: {e}", "should_apply": False}

    def _normalize_text(self, text: str) -> str:
        """Normalize text for fuzzy matching by removing extra spaces and punctuation."""
        import string
        # Remove punctuation except spaces and alphanumeric
        text = ''.join(char if char.isalnum() or char.isspace() else ' ' for char in text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip().lower()
        return text
    
    def _extract_keywords(self, text: str, min_length: int = 3) -> list:
        """Extract meaningful keywords from text, filtering out short/common words."""
        import string
        # Common stop words to ignore
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'how', 'has', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'man', 'end', 'few', 'get', 'his', 'let', 'put', 'say', 'she', 'too', 'use'}
        
        # Remove punctuation and split into words
        cleaned = ''.join(char if char.isalnum() or char.isspace() else ' ' for char in text.lower())
        words = [word.strip() for word in cleaned.split() if len(word.strip()) >= min_length and word.strip() not in stop_words]
        return words
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two strings (0-1 scale)."""
        from difflib import SequenceMatcher
        # Normalize both strings for comparison
        t1 = self._normalize_text(text1)
        t2 = self._normalize_text(text2)
        return SequenceMatcher(None, t1, t2).ratio()
    
    def _find_header_in_content(self, header_text: str, content: str, similarity_threshold: Optional[float] = None) -> Optional[re.Match]:
        """
        Find header using multiple fallback strategies for robustness.
        
        Tries multiple approaches:
        1. Exact regex match (current approach)
        2. Markdown link format match (handles [text](url) format)
        3. Fuzzy similarity match (85% similarity threshold)
        4. Normalized fuzzy match (remove punctuation, normalize spaces) 
        5. Key word sequence match (find meaningful words)
        6. Partial match (find significant portions of header)
        
        Returns the first successful match or None if no strategies work.
        """
        if not header_text or not header_text.strip():
            return None
            
        header_clean = header_text.strip()
        
        # Use provided threshold or instance default
        if similarity_threshold is None:
            similarity_threshold = getattr(self, 'similarity_threshold', 0.85)
        
        # Strategy 1: Exact regex match (original approach)
        try:
            escaped_header = re.escape(header_clean)
            markdown_pattern = rf'^#{1,6}\s*{escaped_header}'
            html_pattern = rf'<h[1-6][^>]*>\s*{escaped_header}\s*</h[1-6]>'
            exact_pattern = f'({markdown_pattern}|{html_pattern})'
            
            match = re.search(exact_pattern, content, re.IGNORECASE | re.MULTILINE)
            if match:
                return match
        except Exception as e:
            pass  # Try next strategy
        
        # Strategy 2: Markdown link format - handles headers with links like ### [Header Text](url)
        try:
            escaped_header = re.escape(header_clean)
            # Match headers that might be in markdown link format
            markdown_link_pattern = rf'^#{1,6}\s*\[{escaped_header}\]\([^)]+\)'
            # Also try without the question mark if present
            header_no_question = header_clean.rstrip('?')
            if header_no_question != header_clean:
                escaped_no_q = re.escape(header_no_question)
                markdown_link_pattern = rf'^#{1,6}\s*\[{escaped_no_q}\??\]\([^)]+\)'
            
            match = re.search(markdown_link_pattern, content, re.IGNORECASE | re.MULTILINE)
            if match:
                return match
        except Exception as e:
            pass  # Try next strategy
        
        # Strategy 3: Fuzzy similarity match - find headers with high similarity
        try:
            # Find all potential headers in the content
            header_pattern = r'^#{1,6}\s+(.+?)$'
            potential_headers = re.finditer(header_pattern, content, re.MULTILINE)
            
            best_match = None
            best_similarity = 0
            
            for match in potential_headers:
                header_in_content = match.group(1).strip()
                similarity = self._calculate_similarity(header_clean, header_in_content)
                
                if similarity >= similarity_threshold and similarity > best_similarity:
                    best_similarity = similarity
                    best_match = match
                    
            if best_match:
                return best_match
                
        except Exception as e:
            pass  # Try next strategy
        
        # Strategy 4: Normalized fuzzy match
        try:
            normalized_header = self._normalize_text(header_clean)
            if normalized_header:
                # Create flexible pattern allowing for extra spaces/chars
                words = normalized_header.split()
                fuzzy_pattern = r'\s*'.join(re.escape(word) for word in words)
                
                # Try both markdown and HTML formats with normalized text
                markdown_fuzzy = rf'^#{1,6}\s*{fuzzy_pattern}'
                html_fuzzy = rf'<h[1-6][^>]*>\s*{fuzzy_pattern}\s*</h[1-6]>'
                fuzzy_pattern_full = f'({markdown_fuzzy}|{html_fuzzy})'
                
                match = re.search(fuzzy_pattern_full, content, re.IGNORECASE | re.MULTILINE)
                if match:
                    return match
        except Exception as e:
            pass  # Try next strategy
        
        # Strategy 5: Key word sequence match
        try:
            keywords = self._extract_keywords(header_clean)
            if len(keywords) >= 2:  # Need at least 2 keywords for meaningful match
                # Create pattern matching key words in sequence with flexible spacing
                keyword_pattern = r'\s+'.join(re.escape(word) for word in keywords[:5])  # Use first 5 keywords max
                
                # Look for this sequence in headers
                markdown_kw = rf'^#{1,6}\s*[^#\n]*{keyword_pattern}[^#\n]*'
                html_kw = rf'<h[1-6][^>]*>[^<]*{keyword_pattern}[^<]*</h[1-6]>'
                keyword_pattern_full = f'({markdown_kw}|{html_kw})'
                
                match = re.search(keyword_pattern_full, content, re.IGNORECASE | re.MULTILINE)
                if match:
                    return match
        except Exception as e:
            pass  # Try next strategy
        
        # Strategy 6: Partial match - look for significant chunks of the header
        try:
            if len(header_clean) > 20:  # Only for longer headers
                # Try first half and last half of header
                mid_point = len(header_clean) // 2
                first_half = header_clean[:mid_point].strip()
                last_half = header_clean[mid_point:].strip()
                
                for partial in [first_half, last_half]:
                    if len(partial) > 10:  # Must be substantial
                        partial_escaped = re.escape(partial)
                        markdown_partial = rf'^#{1,6}\s*[^#\n]*{partial_escaped}[^#\n]*'
                        html_partial = rf'<h[1-6][^>]*>[^<]*{partial_escaped}[^<]*</h[1-6]>'
                        partial_pattern = f'({markdown_partial}|{html_partial})'
                        
                        match = re.search(partial_pattern, content, re.IGNORECASE | re.MULTILINE)
                        if match:
                            return match
        except Exception as e:
            pass  # Try next strategy
        
        # logger.warning(f"Header not found with any strategy: {header_clean}")
        return None

    def _validate_boundaries(self, content: str, analysis: ContentBoundaryAnalysis) -> bool:
        """Validate that the identified boundaries make sense and exist in content."""
        try:
            start_pos = None
            end_pos = None
            
            # Find start boundary position
            if analysis.should_apply_start and analysis.start_header:
                # Try to find the header in the original content
                start_match = self._find_header_in_content(analysis.start_header, content)
                if start_match:
                    start_pos = start_match.start()
                else:
                    logger.warning(f"Start header not found in content: {analysis.start_header}")
                    return False
            
            # Find end boundary position  
            if analysis.should_apply_end and analysis.end_header:
                # Try to find the header in the original content
                end_match = self._find_header_in_content(analysis.end_header, content)
                if end_match:
                    # For end boundary, we want the LAST occurrence
                    # Find all occurrences of the matched pattern
                    all_occurrences = []
                    start_search = 0
                    while True:
                        next_match = self._find_header_in_content(analysis.end_header, content[start_search:])
                        if next_match:
                            actual_pos = start_search + next_match.start()
                            all_occurrences.append(actual_pos)
                            start_search = actual_pos + 1
                        else:
                            break
                    
                    # Use the last occurrence
                    if all_occurrences:
                        end_pos = all_occurrences[-1]
                    else:
                        end_pos = end_match.start()
                else:
                    logger.warning(f"End header not found in content: {analysis.end_header}")
                    return False
            
            # Validate order: start must come before end
            if start_pos is not None and end_pos is not None:
                if start_pos >= end_pos:
                    logger.warning(f"Start position ({start_pos}) >= end position ({end_pos})")
                    return False
                
                # Ensure resulting content isn't too small
                min_size = getattr(self, 'min_truncated_size', 500)
                truncated_length = end_pos - start_pos
                if truncated_length < min_size:
                    logger.warning(f"Truncated content too small: {truncated_length} chars (min: {min_size})")
                    return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Boundary validation error: {e}")
            return False

    def _apply_boundaries(self, content: str, analysis: ContentBoundaryAnalysis) -> str:
        """Apply the validated boundaries to truncate content."""
        try:
            result_content = content
            
            # Apply start boundary
            if analysis.should_apply_start and analysis.start_header:
                start_match = self._find_header_in_content(analysis.start_header, content)
                if start_match:
                    result_content = content[start_match.start():]
                    logger.info(f"Applied start boundary at header: {analysis.start_header}")
            
            # Apply end boundary
            if analysis.should_apply_end and analysis.end_header:
                # Find the end header in the (potentially truncated) result content
                end_match = self._find_header_in_content(analysis.end_header, result_content)
                if end_match:
                    # Include the end header but cut after its content section
                    end_pos = end_match.end()
                    # Find the next header or end of content
                    remaining_content = result_content[end_pos:]
                    # Pattern to match any header (markdown or HTML)
                    next_header_pattern = r'(^#{1,6}\s+|<h[1-6][^>]*>)'
                    next_header_match = re.search(next_header_pattern, remaining_content, re.MULTILINE)
                    if next_header_match:
                        end_pos += next_header_match.start()
                    else:
                        end_pos = len(result_content)
                    
                    result_content = result_content[:end_pos]
                    logger.info(f"Applied end boundary at header: {analysis.end_header}")
            
            return result_content
            
        except Exception as e:
            logger.warning(f"Error applying boundaries: {e}")
            return content

    def _clean_urls_and_images(self, content: str) -> str:
        """Clean URLs and image sources aggressively to help AI focus on content structure."""
        # More aggressive cleaning for navigation-heavy sites
        
        # Clean ALL markdown links (not just long ones) - keep text but remove URLs
        content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
        
        # Clean ALL markdown images
        content = re.sub(r'!\[([^\]]*)\]\([^)]+\)', lambda m: f'[IMG: {m.group(1)}]' if m.group(1) else '[IMG]', content)
        
        # Clean HTML links and images (if any HTML remains)
        content = re.sub(r'href="[^"]*"', 'href="#"', content)
        content = re.sub(r'src="[^"]*"', 'src="#"', content) 
        content = re.sub(r'data-[a-z-]+="[^"]*"', '', content)
        
        # Clean any standalone URLs
        content = re.sub(r'https?://[^\s\)]+', '[URL]', content)
        
        # Clean phone numbers (common in nav)
        content = re.sub(r'tel:\d+', '[PHONE]', content)
        content = re.sub(r'\d{3}-\d{3}-\d{4}', '[PHONE]', content)
        content = re.sub(r'\d{3}-\d{4}-\d{4}', '[PHONE]', content)
        
        # Collapse excessive whitespace from removed elements
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        return content

    async def analyze_boundaries(self, content: str, analysis_length: int = 5000, min_confidence: int = 3) -> Tuple[str, ContentBoundaryAnalysis]:
        """
        Main method to analyze and apply content boundaries.
        
        Args:
            content: Full content to analyze
            analysis_length: Characters to analyze at each end
            min_confidence: Minimum confidence to apply boundaries
            
        Returns:
            Tuple of (processed_content, analysis)
        """
        if len(content) < self.min_content_size:  # Skip for very short content
            return content, None
        
        try:
            # Extract content sections for analysis
            content_start = content[:analysis_length]
            content_end = content[-analysis_length:]
            
            # Clean URLs and images to help AI focus on content structure  
            content_start_cleaned = self._clean_urls_and_images(content_start)
            content_end_cleaned = self._clean_urls_and_images(content_end)

            # Run both analyses concurrently with cleaned content
            start_task = self._analyze_start_boundary(content_start_cleaned)
            end_task = self._analyze_end_boundary(content_end_cleaned)
            
            start_result, end_result = await asyncio.gather(start_task, end_task, return_exceptions=True)
            
            # Handle exceptions
            if isinstance(start_result, Exception):
                logger.warning(f"Start analysis failed: {start_result}")
                start_result = {"header": None, "confidence": 1, "reasoning": "Analysis failed", "should_apply": False}
            
            if isinstance(end_result, Exception):
                logger.warning(f"End analysis failed: {end_result}")
                end_result = {"header": None, "confidence": 1, "reasoning": "Analysis failed", "should_apply": False}
            
            # Create analysis object
            analysis = ContentBoundaryAnalysis(
                start_header=start_result.get("header"),
                end_header=end_result.get("header"),
                start_confidence=start_result.get("confidence", 1),
                end_confidence=end_result.get("confidence", 1),
                start_reasoning=start_result.get("reasoning", "No analysis"),
                end_reasoning=end_result.get("reasoning", "No analysis"),
                should_apply_start=(
                    start_result.get("should_apply", False) and 
                    start_result.get("confidence", 1) >= min_confidence
                ),
                should_apply_end=(
                    end_result.get("should_apply", False) and 
                    end_result.get("confidence", 1) >= min_confidence
                )
            )
            
            logger.info(f"Boundary analysis - Start: {analysis.should_apply_start} ({analysis.start_confidence}/5), End: {analysis.should_apply_end} ({analysis.end_confidence}/5)")
            
            # Validate boundaries
            if not self._validate_boundaries(content, analysis):
                logger.warning("Boundary validation failed, using original content")
                return content, analysis
            
            # Apply boundaries if validation passed
            if analysis.should_apply_start or analysis.should_apply_end:
                preprocessed_content = self._apply_boundaries(content, analysis)
                chars_removed = len(content) - len(preprocessed_content)
                logger.info(f"Content preprocessing complete: removed {chars_removed} characters ({chars_removed/len(content)*100:.1f}%)")
                return preprocessed_content, analysis
            else:
                logger.info("No boundaries to apply, using original content")
                return content, analysis
                
        except Exception as e:
            logger.warning(f"Content boundary analysis failed: {e}")
            return content, None