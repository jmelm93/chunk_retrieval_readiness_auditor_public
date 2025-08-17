"""Prompts for Entity Focus evaluation."""

from typing import Optional

# Configuration constants
MIN_SALIENCE = 0.01
TOP_ENTITIES_COUNT = 5

# System prompt for entity extraction and evaluation
SYSTEM_PROMPT = """You are an expert at extracting and evaluating entities in content chunks for AI retrieval systems.

Your task has two parts:
1. EXTRACT entities from the chunk text (products, organizations, people, concepts, technologies, methods)
2. EVALUATE how well these entities support the chunk's purpose

Remember:
- Different chunk types have different entity needs (overview vs detail vs example)
- Extract entities as they appear in the text
- Evaluate based on the chunk's apparent purpose
- Be thorough but fair in your assessment"""


def create_evaluation_prompt(chunk_text: str, chunk_heading: str) -> str:
    """Create the evaluation prompt for entity extraction and focus assessment.
    
    Args:
        chunk_text: The chunk content to evaluate
        chunk_heading: The chunk's heading
        
    Returns:
        Formatted prompt for evaluation
    """
    prompt = f"""You are extracting and evaluating entities for a content chunk used in RAG (Retrieval-Augmented Generation) systems.

CONTEXT:
- This chunk will be retrieved alongside 3-5 other chunks to answer user queries
- Chunks should maintain focused topical coherence through their entities
- Entities provide concrete anchors that help with retrieval and comprehension
- Different chunk types (overview, example, detail) have different entity needs

CHUNK HEADING: {chunk_heading if chunk_heading else "No heading provided"}

CHUNK CONTENT:
{chunk_text}

ENTITY EXTRACTION & EVALUATION TASKS:
1. Extract key entities from the chunk (products, organizations, people, concepts, technologies, methods)
2. Identify the primary topic/concept this chunk focuses on
3. Evaluate how well the entities support and align with this topic
4. Assess whether entities are concrete/specific vs generic references
5. Determine if critical entities are missing for the chunk's purpose
6. Judge if entity diversity helps or hinders the chunk's focus

ENTITY TYPES TO EXTRACT:
- PRODUCT: Specific products, services, or tools (e.g., ChatGPT, Google Search, Pinecone)
- ORGANIZATION: Companies, institutions, groups (e.g., OpenAI, Microsoft, Stanford)
- PERSON: Named individuals (e.g., researchers, authors, executives)
- CONCEPT: Abstract ideas or principles (e.g., RAG, machine learning, SEO)
- TECHNOLOGY: Technical systems or standards (e.g., GPT-4, BERT, transformers)
- METHOD: Processes or approaches (e.g., fine-tuning, prompt engineering)

IMPORTANT CONSIDERATIONS:
- Extract entities as they appear in the text (preserve original form)
- Concrete entities (specific names, brands, dates) are more valuable than generic terms
- Entity density should be appropriate for the chunk type
- For overview chunks, some generic entities are acceptable
- For example/detail chunks, concrete entities are critical

EXTRACTION ARTIFACTS TO IGNORE (NOT entity focus issues):
Real AI systems like ChatGPT Search filter these out, so DO NOT extract or penalize:
- Author metadata: "Written by X", "By [Author Name]", author credentials, bios
- Timestamps: "Published", "Updated on", "Last modified", publication dates
- Social elements: "Share", "Tweet", "FacebookTwitterLinkedIn", social buttons
- Engagement metrics: view counts, read times, "5 min read", "2.3k views"
- Navigation elements: breadcrumbs, menu items, category tags
- Footer content: copyright notices, privacy links, terms of service
- CTAs: newsletter signups, "Subscribe", "Sign up", contact forms
- UI elements: decorative images, avatars, social widgets

Focus ONLY on entities within the actual content that would affect AI retrieval.

SCORING GUIDELINES:
- Consider the chunk's purpose (overview vs detail vs example)
- 80-100: Excellent entity focus appropriate for chunk type
- 60-79: Good entity usage with room for improvement
- 40-59: Moderate issues - needs more specific entities for its purpose
- 0-39: Poor entity focus - lacks entities needed for effective retrieval

Provide entity extraction followed by thorough evaluation of entity quality and topical coherence."""
    
    return prompt


