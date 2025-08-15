"""AI-based content validation for filtering low-value chunks."""

import os
import re
import asyncio
from typing import Optional, Tuple
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from loguru import logger


class ContentValidation(BaseModel):
    """Structured output for content validation decision."""
    should_analyze: bool = Field(
        description="Whether this chunk contains substantive content worth analyzing"
    )
    reason: str = Field(
        description="Brief explanation of the decision (max 50 chars)"
    )
    content_type: str = Field(
        description="Type of content: content, navigation, links, form, boilerplate, footer_mixed, author_bio, site_navigation, too_short, heading_only, list_fragment, loading_message, breadcrumb"
    )


class ContentValidator:
    """Validate whether chunks contain substantive content worth analyzing."""
    
    VALIDATION_PROMPT = """You evaluate whether text chunks contain substantive content worth analyzing for retrieval readiness.

IMPORTANT: Check for MIXED CHUNKS that combine a small amount of real content with footer/navigation material.
If >50% of the chunk is boilerplate, navigation, or metadata, mark it as should_analyze=false.

SKIP chunks that are primarily (should_analyze=false):
- Navigation elements: "Skip to main content", breadcrumbs, menu items
- Link lists: Footer links, sidebar navigation, related articles lists
- Forms: Sign-in forms, search boxes, newsletter signups
- Boilerplate: Copyright notices, legal disclaimers, cookie notices
- Author bios with site navigation: Author details followed by site menus
- Mixed footer chunks: 1-2 paragraphs of content followed by extensive footer
- Site-wide navigation: Tools, Resources, Company, About us, Contact sections
- Social media link collections
- Copyright and legal text

ANALYZE chunks that contain (should_analyze=true):
- Article content with substantive paragraphs (at least 3-4 sentences)
- Documentation or tutorials with detailed instructions
- Product descriptions with meaningful details
- FAQs or Q&A content with complete answers
- Reviews or testimonials with substance
- News or blog posts with actual article body
- Technical content with explanations or code

Examples to SKIP:

1. "The Bottom Line: Stay Adaptable
   
   One paragraph of advice here.
   
   John Smith
   Founder of Example.com
   Expert in various fields.
   
   Tools
   - All Tools
   - Analysis
   
   Resources  
   - Blog
   - Contact
   
   © 2024 Example"
   -> footer_mixed, mostly navigation/bio
   
2. "Final Thoughts
   
   Thanks for reading!
   
   Jane Doe
   20 years experience in tech
   Speaker at conferences
   
   Newsletter: [Sign up]
   Follow us: [Twitter] [LinkedIn]
   
   Privacy Policy | Terms"
   -> footer_mixed, minimal content with bio/links

3. "© 2024 Company | Privacy Policy | Terms of Service"
   -> boilerplate footer

4. "Jason Melman
   Founder of SEO Workflows
   VP of SEO for DEPT
   Expert in SEO, database engineering"
   -> author_bio, no article content

Examples to ANALYZE:

1. "The penny costs 4 cents to produce, making it economically inefficient. This has led to proposals to eliminate it from circulation. Several countries have already removed their smallest denominations, reporting minimal economic impact and simplified transactions."
   -> substantive content about economics

2. "To optimize for AI retrieval, focus on semantic coherence within chunks. Each section should be self-contained yet connect to the broader topic. Use clear headers, maintain entity consistency, and ensure each chunk can contribute meaningfully to multi-chunk retrieval scenarios."
   -> detailed technical guidance

3. "Our latest security update addresses three critical vulnerabilities. The first affects user authentication, potentially allowing session hijacking. The second involves SQL injection in search queries. The third relates to cross-site scripting in comment sections. All users should update immediately."
   -> important technical/security content

Evaluate this chunk:
{chunk_text}"""

    def __init__(self, 
                 model: str = "gpt-5-nano",
                 api_key: Optional[str] = None,
                 config: Optional[any] = None,
                 max_concurrent: int = 10):
        """
        Initialize the content validator.
        
        Args:
            model: OpenAI model to use for validation
            api_key: OpenAI API key (uses env if not provided)
            config: Optional configuration object
            max_concurrent: Maximum concurrent API calls
        """
        self.config = config
        
        # Determine model from config or use default
        if config and hasattr(config, 'models'):
            if config.models.overrides and 'content_filter' in config.models.overrides:
                self.model = config.models.overrides['content_filter']
            elif config.filtering and hasattr(config.filtering, 'model'):
                self.model = config.filtering.model
            else:
                self.model = model
        else:
            self.model = model
            
        # Initialize OpenAI client
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required for content validation")
            
        self.client = AsyncOpenAI(api_key=self.api_key)
        
        # Add semaphore to limit concurrent API calls
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # Get filtering settings from config
        self.strict_filtering = False
        self.boilerplate_threshold = 0.5
        self.min_char_length = 150
        self.min_word_count = 20
        self.min_sentence_count = 2
        
        if config and hasattr(config, 'filtering'):
            self.strict_filtering = getattr(config.filtering, 'strict_filtering', False)
            self.boilerplate_threshold = getattr(config.filtering, 'boilerplate_threshold', 0.5)
            self.min_char_length = getattr(config.filtering, 'min_char_length', 150)
            self.min_word_count = getattr(config.filtering, 'min_word_count', 20)
            self.min_sentence_count = getattr(config.filtering, 'min_sentence_count', 2)
        
        logger.info(f"ContentValidator initialized with model: {self.model}, max_concurrent: {max_concurrent}, strict: {self.strict_filtering}, min_chars: {self.min_char_length}")
    
    def _detect_footer_patterns(self, text: str) -> Tuple[bool, float, str]:
        """
        Detect common footer/navigation patterns using regex.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (is_likely_footer, confidence_score, pattern_type)
        """
        patterns = {
            'copyright': r'(?i)(©|\(c\)|copyright)\s+\d{4}|all rights reserved',
            'privacy_terms': r'(?i)(privacy policy|terms of service|terms & conditions|cookie policy)',
            'navigation_menu': r'(?i)(about us|contact us|careers|company|resources|tools|products|services)\s*\n',
            'social_media': r'(?i)(facebook|twitter|linkedin|youtube|instagram|tiktok)[\s\|,]{1,3}(facebook|twitter|linkedin|youtube|instagram)',
            'author_bio': r'(?i)(founder of|ceo of|vp of|expert in|years? experience|speaker at)',
            'newsletter': r'(?i)(subscribe|newsletter|sign up|email updates|stay updated)',
            'footer_sections': r'(?i)^(tools|resources|company|support|legal|follow us|connect)\s*$'
        }
        
        text_lower = text.lower()
        lines = text.split('\n')
        total_lines = len(lines)
        
        # Count pattern matches
        pattern_matches = {}
        footer_line_count = 0
        
        for pattern_name, pattern in patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                pattern_matches[pattern_name] = len(matches)
                # Count lines containing these patterns
                for line in lines:
                    if re.search(pattern, line):
                        footer_line_count += 1
                        break
        
        # Calculate confidence based on pattern density
        if not pattern_matches:
            return False, 0.0, "none"
        
        # Strong indicators
        strong_indicators = ['copyright', 'privacy_terms', 'footer_sections']
        has_strong = any(p in pattern_matches for p in strong_indicators)
        
        # Calculate footer ratio
        footer_ratio = footer_line_count / total_lines if total_lines > 0 else 0
        
        # Determine if it's likely footer content
        if has_strong and footer_ratio > 0.3:
            confidence = min(0.9, footer_ratio + 0.3)
            pattern_type = "footer"
        elif 'author_bio' in pattern_matches and footer_ratio > 0.4:
            confidence = min(0.8, footer_ratio + 0.2)
            pattern_type = "author_bio"
        elif len(pattern_matches) >= 3:
            confidence = min(0.7, footer_ratio + 0.2)
            pattern_type = "mixed_footer"
        else:
            confidence = footer_ratio
            pattern_type = "partial"
        
        is_footer = confidence > self.boilerplate_threshold
        
        return is_footer, confidence, pattern_type
    
    def _quick_content_check(self, text: str) -> Optional[ContentValidation]:
        """
        Quick pattern-based pre-check before API call.
        
        Args:
            text: Text to check
            
        Returns:
            ContentValidation if definitely footer/nav/insufficient, None if needs AI check
        """
        # Clean and prepare text
        clean_text = text.strip()
        
        # 1. Character length check
        if len(clean_text) < self.min_char_length:
            return ContentValidation(
                should_analyze=False,
                reason=f"Too short ({len(clean_text)} chars < {self.min_char_length})",
                content_type="too_short"
            )
        
        # 2. Word count check
        words = clean_text.split()
        if len(words) < self.min_word_count:
            return ContentValidation(
                should_analyze=False,
                reason=f"Too few words ({len(words)} < {self.min_word_count})",
                content_type="too_short"
            )
        
        # 3. Sentence count check
        sentences = [s.strip() for s in re.split(r'[.!?]+', clean_text) if len(s.strip()) > 10]
        if len(sentences) < self.min_sentence_count:
            return ContentValidation(
                should_analyze=False,
                reason=f"Insufficient sentences ({len(sentences)} < {self.min_sentence_count})",
                content_type="fragment"
            )
        
        # 4. Check for heading-only chunks (single line under 100 chars)
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if len(lines) == 1 and len(lines[0]) < 100:
            return ContentValidation(
                should_analyze=False,
                reason="Heading without content",
                content_type="heading_only"
            )
        
        # 5. Check for excessive whitespace
        if clean_text:
            whitespace_ratio = len(re.findall(r'\s', text)) / len(text)
            if whitespace_ratio > 0.5:
                return ContentValidation(
                    should_analyze=False,
                    reason="Excessive whitespace",
                    content_type="fragment"
                )
        
        # 6. Check for loading/error messages
        loading_patterns = r'(?i)(loading\.\.\.|please wait|error \d{3}|not found|coming soon|under construction|page not found)'
        if re.search(loading_patterns, clean_text) and len(clean_text) < 200:
            return ContentValidation(
                should_analyze=False,
                reason="UI status message",
                content_type="loading_message"
            )
        
        # 7. Check for breadcrumb navigation
        breadcrumb_pattern = r'(?i)(home\s*[>»/]|\s*[>»/]\s*\w+\s*[>»/]\s*\w+)'
        if re.search(breadcrumb_pattern, clean_text) and len(lines) <= 2:
            return ContentValidation(
                should_analyze=False,
                reason="Breadcrumb navigation",
                content_type="breadcrumb"
            )
        
        # 8. Check for list fragments (just bullet points without context)
        bullet_lines = [l for l in lines if re.match(r'^[•\-\*\d\.\)]\s', l)]
        if len(bullet_lines) == len(lines) and len(clean_text) < 200:
            return ContentValidation(
                should_analyze=False,
                reason="List fragment without context",
                content_type="list_fragment"
            )
        
        # Check for footer patterns
        is_footer, confidence, pattern_type = self._detect_footer_patterns(text)
        
        # In strict mode, filter anything that looks like footer
        if self.strict_filtering and is_footer:
            return ContentValidation(
                should_analyze=False,
                reason=f"Footer/nav patterns detected ({int(confidence*100)}% conf)",
                content_type=pattern_type
            )
        
        # High confidence footer detection
        if confidence > 0.75:
            # Check if there's substantial content before the footer
            lines = text.split('\n')
            content_lines = []
            for line in lines:
                # Stop when we hit obvious footer content
                if re.search(r'(?i)(©|copyright|privacy policy|terms of service)', line):
                    break
                if line.strip():
                    content_lines.append(line)
            
            # If less than 3 lines of actual content before footer, skip
            if len(content_lines) < 3:
                return ContentValidation(
                    should_analyze=False,
                    reason=f"Mostly {pattern_type} content",
                    content_type=f"{pattern_type}_mixed" if content_lines else pattern_type
                )
        
        # Let AI decide for uncertain cases
        return None
    
    async def validate_chunk(self, text: str) -> ContentValidation:
        """
        Validate whether a chunk contains substantive content.
        
        Args:
            text: Chunk text to validate
            
        Returns:
            ContentValidation with decision and reasoning
        """
        # Try quick pattern-based check first
        quick_result = self._quick_content_check(text)
        if quick_result:
            logger.debug(f"Quick filter: {quick_result.content_type} - {quick_result.reason}")
            return quick_result
        
        # Truncate very long chunks for validation (we just need a sample)
        sample_text = text[:3000] if len(text) > 3000 else text

        # Use semaphore to limit concurrent API calls
        async with self.semaphore:
            try:
                # Use structured output for reliable parsing
                response = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.VALIDATION_PROMPT.format(chunk_text=sample_text)
                    }
                ],
                response_format=ContentValidation,
                # max_completion_tokens=100,
                # temperature=0.1  # Low temperature for consistent decisions
            )
            
                result = response.choices[0].message.parsed
                
                # Log decision for transparency
                if not result.should_analyze:
                    logger.debug(f"AI filter: {result.content_type} - {result.reason}")
                
                return result
                
            except Exception as e:
                # On error, default to analyzing (fail open, not closed)
                logger.error(f"Content validation failed: {e}")
                return ContentValidation(
                    should_analyze=True,
                    reason="Validation error - defaulting to analyze",
                    content_type="unknown"
                )
    
    def validate_chunk_sync(self, text: str) -> ContentValidation:
        """
        Synchronous version of validate_chunk.
        
        Args:
            text: Chunk text to validate
            
        Returns:
            ContentValidation with decision
        """
        import asyncio
        return asyncio.run(self.validate_chunk(text))