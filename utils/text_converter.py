"""Text conversion utilities for RAG-appropriate content processing.

This module provides utilities to convert markdown/HTML content to plain text,
following industry best practices where RAG systems embed and retrieve plain text
while using structure (headers) only for chunking boundaries.
"""

import re
from typing import Optional
from loguru import logger

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    logger.warning("BeautifulSoup not available for HTML processing")

try:
    import markdown_it
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
    logger.warning("markdown-it-py library not available")


def convert_to_plain_text(content: str, preserve_structure: bool = False) -> str:
    """
    Convert markdown/HTML content to plain text for RAG evaluation.
    
    This follows industry best practices where entity extraction and embedding
    are performed on plain text to match what commercial RAG systems like
    ChatGPT, Gemini, and Perplexity actually use.
    
    Args:
        content: The content to convert (may be markdown, HTML, or plain text)
        preserve_structure: If True, keeps minimal structure markers (for display)
        
    Returns:
        Plain text version of the content suitable for RAG evaluation
    """
    if not content:
        return ""
    
    # Step 1: Convert markdown to HTML if needed
    html_content = content
    
    # Check if content looks like markdown (has markdown indicators)
    markdown_indicators = [
        '###',  # Headers
        '**',   # Bold
        '```',  # Code blocks
        '[',    # Links (could be false positive)
        '![',   # Images
        '- ',   # Lists (at line start)
        '* ',   # Lists (at line start)
        '1. ',  # Numbered lists
    ]
    
    # Simple heuristic: if we see headers or multiple markdown indicators, it's likely markdown
    is_markdown = False
    if '#' in content and content.strip().startswith('#'):
        is_markdown = True
    else:
        indicator_count = sum(1 for indicator in markdown_indicators if indicator in content)
        if indicator_count >= 2:
            is_markdown = True
    
    # Convert markdown to HTML first for consistent processing
    if is_markdown and MARKDOWN_AVAILABLE:
        try:
            md = markdown_it.MarkdownIt()
            html_content = md.render(content)
        except Exception as e:
            logger.debug(f"Markdown conversion failed, treating as HTML/plain: {e}")
            html_content = content
    
    # Step 2: Extract plain text from HTML
    if BS4_AVAILABLE and ('<' in html_content and '>' in html_content):
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements completely
            for element in soup(['script', 'style', 'meta', 'link', 'noscript']):
                element.decompose()
            
            # Remove comments
            for comment in soup.find_all(string=lambda text: isinstance(text, str) and '<!--' in text):
                comment.extract()
            
            if preserve_structure:
                # Keep headers with simple markers
                for i in range(1, 7):
                    for header in soup.find_all(f'h{i}'):
                        header.string = f"\n{'#' * i} {header.get_text(strip=True)}\n"
                
                # Keep list structure
                for li in soup.find_all('li'):
                    li.string = f"• {li.get_text(strip=True)}"
                
                # Add spacing for paragraphs
                for p in soup.find_all('p'):
                    p.string = f"\n{p.get_text(strip=True)}\n"
            
            # Get text with proper spacing
            text = soup.get_text(separator=' ', strip=True)
            
        except Exception as e:
            logger.debug(f"HTML parsing failed, using fallback: {e}")
            text = html_content
    else:
        text = html_content
    
    # Step 3: Clean up the text
    
    # Remove any remaining HTML entities
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)
    text = re.sub(r'&#\d+;', ' ', text)
    text = re.sub(r'&x[0-9a-fA-F]+;', ' ', text)
    
    # Remove any remaining markdown syntax if not already processed
    if not is_markdown or not MARKDOWN_AVAILABLE:
        # Remove code blocks
        text = re.sub(r'```[^`]*```', '', text, flags=re.MULTILINE | re.DOTALL)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # Remove links but keep text
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', text)
        
        # Remove emphasis
        text = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', text)
        text = re.sub(r'_{1,2}([^_]+)_{1,2}', r'\1', text)
        
        if not preserve_structure:
            # Remove headers
            text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Clean up URLs (common issue in entity extraction)
    # Keep domain names but remove full URLs
    text = re.sub(r'https?://[^\s<>"{}|\\^`\[\]]+', lambda m: m.group().split('/')[2] if '/' in m.group() else '', text)
    
    # Normalize whitespace while preserving paragraph structure
    # First, normalize spaces within lines (but not newlines)
    lines = text.split('\n')
    normalized_lines = []
    for line in lines:
        # Normalize multiple spaces to single space within each line
        line = re.sub(r'[ \t]+', ' ', line.strip())
        normalized_lines.append(line)
    
    # Join back with newlines
    text = '\n'.join(normalized_lines)
    
    # Now clean up excessive newlines (more than 2 consecutive)
    # This preserves paragraph breaks but removes excessive spacing
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove empty lines that are just whitespace
    lines = text.split('\n')
    text = '\n'.join(line for line in lines if line.strip() or line == '')
    
    # Final cleanup
    text = text.strip()
    
    return text


def extract_headers_from_content(content: str) -> list:
    """
    Extract headers from markdown/HTML content for structural analysis.
    
    Args:
        content: The content to extract headers from
        
    Returns:
        List of headers with their levels
    """
    headers = []
    
    # Try HTML parsing first
    if BS4_AVAILABLE and '<h' in content.lower():
        try:
            soup = BeautifulSoup(content, 'html.parser')
            for i in range(1, 7):
                for header in soup.find_all(f'h{i}'):
                    headers.append({
                        'level': i,
                        'text': header.get_text(strip=True)
                    })
            if headers:
                return headers
        except:
            pass
    
    # Fallback to markdown parsing
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('#'):
            # Count the number of # symbols
            level = len(line) - len(line.lstrip('#'))
            if 1 <= level <= 6:
                text = line.lstrip('#').strip()
                if text:
                    headers.append({
                        'level': level,
                        'text': text
                    })
    
    return headers


def truncate_content(text: str, max_length: int = 3000) -> str:
    """Truncate content intelligently, avoiding cutting inside code fences.
    
    This improved version:
    1. Avoids cutting inside code fences (```)
    2. Prefers sentence/paragraph boundaries
    3. Uses sentence boundaries over arbitrary cuts
    
    Args:
        text: Text to potentially truncate
        max_length: Maximum length in characters
        
    Returns:
        Truncated text with "(...truncated)" marker if truncated
    """
    if len(text) <= max_length:
        return text
    
    # Initial cut at max_length
    cut = text[:max_length]
    
    # Check if we're cutting inside code fences
    if cut.count("```") % 2 == 1:
        # We're inside a code fence, find the last complete fence
        back = cut.rfind("```")
        if back > 0:
            cut = cut[:back]
    
    # Try to find a good boundary (sentence or paragraph end)
    # Look for sentence endings first
    last_period = cut.rfind(".")
    last_newline = cut.rfind("\n")
    
    # Use the best boundary if it's not too far back (within 30% of max_length)
    best_boundary = max(last_period, last_newline)
    if best_boundary > max_length * 0.7:
        cut = cut[:best_boundary + 1]
    
    return cut.strip() + " (...truncated)"


def estimate_token_count(text: str, chars_per_token: float = 4.0) -> int:
    """Estimate token count using character-based heuristic.
    
    This provides a rough estimate without requiring a tokenizer.
    GPT models average ~4 characters per token for English text.
    
    Args:
        text: Text to estimate tokens for
        chars_per_token: Average characters per token (default 4.0 for GPT models)
        
    Returns:
        Estimated token count
    """
    if not text:
        return 0
    
    return max(1, int(len(text) / chars_per_token))


def get_text_metadata(text: str) -> dict:
    """Extract useful metadata from text for evaluation context.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with text metadata
    """
    if not text:
        return {
            "char_count": 0,
            "word_count": 0,
            "line_count": 0,
            "token_count_estimate": 0,
            "has_code_blocks": False,
            "code_block_count": 0
        }
    
    # Basic counts
    char_count = len(text)
    word_count = len(text.split())
    line_count = text.count('\n') + 1
    
    # Code block detection
    code_block_count = text.count('```')
    has_code_blocks = code_block_count > 0
    
    return {
        "char_count": char_count,
        "word_count": word_count,
        "line_count": line_count,
        "token_count_estimate": estimate_token_count(text),
        "has_code_blocks": has_code_blocks,
        "code_block_count": code_block_count // 2  # Pairs of opening/closing
    }


def load_ignore_artifacts() -> str:
    """Load the shared ignore artifacts text for embedding in prompts.
    
    Returns:
        The ignore artifacts text to embed in system prompts
    """
    try:
        import os
        # Look for the artifacts file in evaluators_v2/shared directory
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        artifacts_path = os.path.join(current_dir, "evaluators_v2", "shared", "ignore_web_artifacts.md")
        
        if os.path.exists(artifacts_path):
            with open(artifacts_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
    except Exception as e:
        logger.debug(f"Could not load ignore_web_artifacts.md: {e}")
    
    # Fallback to hardcoded version
    return """Ignore these extraction artifacts (do not penalize or extract):
- Author bylines, bios, avatars (e.g., "Written by…")
- Timestamps/dates ("Published", "Updated on", "Last modified")
- Share button text ("FacebookTwitterLinkedIn", "Share this article"), social widgets
- Engagement metrics (view counts, read time, likes)
- Navigation (menus, breadcrumbs, category tags, "Skip to content")
- Footer content (copyright, privacy/terms)
- CTAs (newsletter signups, subscribe forms, contact forms)
- Related content ("You may also like", recommended posts)
- Decorative media (hero images, author photos)"""