"""High quality test cases expected to score well."""

HIGH_QUALITY_CASES = [
    {
        "id": "high_001",
        "name": "Well-structured API documentation",
        "category": "high_quality",
        "chunk_heading": "Authentication with API Keys",
        "chunk_text": """To authenticate with our API, you'll need to include your API key in the request headers.

## Obtaining Your API Key

1. Log in to your dashboard at https://api.example.com/dashboard
2. Navigate to Settings > API Keys
3. Click "Generate New Key" and provide a descriptive name
4. Copy the generated key immediately (it won't be shown again)

## Using Your API Key

Include your API key in the `Authorization` header of every request:

```
Authorization: Bearer YOUR_API_KEY_HERE
```

## Example Request

Here's a complete example using curl:

```bash
curl -X GET https://api.example.com/v1/users \
  -H "Authorization: Bearer sk_live_abc123xyz789" \
  -H "Content-Type: application/json"
```

## Security Best Practices

- Never commit API keys to version control
- Use environment variables to store keys in production
- Rotate keys regularly (recommended: every 90 days)
- Restrict key permissions to only required endpoints
- Monitor key usage through the dashboard

If you suspect your key has been compromised, revoke it immediately through the dashboard and generate a new one.""",
        "expected": {
            "query_answer": {"min": 75, "max": 95, "notes": "Complete, actionable content"},
            "llm_rubric": {"min": 70, "max": 90, "notes": "Well-structured with examples"},
            "structure_quality": {"min": 75, "max": 95, "notes": "Clear headings and lists"},
            "entity_focus": {"min": 65, "max": 85, "notes": "Good mix of concepts and specifics"},
            "overall": {"min": 70, "max": 90}
        },
        "notes": "Comprehensive API documentation with clear structure, examples, and actionable steps"
    },
    
    {
        "id": "high_002",
        "name": "FAQ section with clear Q&A pairs",
        "category": "high_quality",
        "chunk_heading": "Frequently Asked Questions about RAG Systems",
        "chunk_text": """## What is RAG (Retrieval-Augmented Generation)?

RAG combines the power of large language models with external knowledge retrieval. Instead of relying solely on training data, RAG systems fetch relevant information from a knowledge base before generating responses. This approach reduces hallucinations and provides more accurate, up-to-date answers.

## How does RAG differ from fine-tuning?

While fine-tuning permanently modifies a model's weights with new knowledge, RAG keeps the base model unchanged and dynamically retrieves information at inference time. Key differences include:

- **Update frequency**: RAG knowledge bases can be updated instantly; fine-tuning requires retraining
- **Cost**: RAG is more cost-effective for frequently changing information
- **Transparency**: RAG can cite sources; fine-tuned models cannot explain their knowledge origin
- **Scale**: RAG can handle millions of documents without model size increase

## What are the main components of a RAG system?

A typical RAG system consists of three core components:

1. **Document Store**: Where your knowledge base lives (vector database like Pinecone, Weaviate, or Chroma)
2. **Retriever**: Fetches relevant documents based on query similarity
3. **Generator**: LLM that synthesizes retrieved information into coherent responses

## When should I use RAG instead of direct LLM queries?

Consider RAG when you need:
- Domain-specific or proprietary information
- Frequently updated content
- Source attribution and transparency
- Reduced hallucination risk
- Cost-effective scaling of knowledge""",
        "expected": {
            "query_answer": {"min": 80, "max": 100, "notes": "Directly answers common questions"},
            "llm_rubric": {"min": 75, "max": 95, "notes": "Perfect Q&A structure"},
            "structure_quality": {"min": 80, "max": 100, "notes": "Excellent FAQ format"},
            "entity_focus": {"min": 70, "max": 90, "notes": "Strong RAG-related entities"},
            "overall": {"min": 75, "max": 95}
        },
        "notes": "Well-structured FAQ with clear questions and comprehensive answers"
    },
    
    {
        "id": "high_003",
        "name": "Product feature description with entities",
        "category": "high_quality",
        "chunk_heading": "GitHub Copilot: AI-Powered Code Completion",
        "chunk_text": """GitHub Copilot is an AI pair programmer that helps developers write code faster and with fewer errors. Powered by OpenAI's Codex model, Copilot suggests entire lines or blocks of code as you type.

## Key Features

**Contextual Code Suggestions**: Copilot analyzes your current file, imported dependencies, and coding patterns to provide relevant suggestions. It understands variable names, function signatures, and comments to generate appropriate code.

**Multi-Language Support**: Works with Python, JavaScript, TypeScript, Ruby, Go, C++, C#, Java, PHP, and dozens more. Copilot adapts its suggestions to match language-specific idioms and best practices.

**Test Generation**: Automatically generates unit tests based on your implementation. Simply write a function, and Copilot can suggest comprehensive test cases including edge cases.

**Documentation Writing**: Converts code into clear documentation. Add a comment describing what you want to document, and Copilot generates detailed docstrings or README sections.

## Integration and Compatibility

Copilot integrates seamlessly with:
- Visual Studio Code
- Visual Studio
- Neovim
- JetBrains IDEs (IntelliJ IDEA, PyCharm, WebStorm, etc.)

## Pricing Tiers

- **Individual**: $10/month or $100/year
- **Business**: $19/user/month with centralized billing
- **Enterprise**: Custom pricing with advanced security features""",
        "expected": {
            "query_answer": {"min": 75, "max": 95, "notes": "Comprehensive product overview"},
            "llm_rubric": {"min": 70, "max": 90, "notes": "Good structure and detail"},
            "structure_quality": {"min": 75, "max": 95, "notes": "Clear sections and formatting"},
            "entity_focus": {"min": 80, "max": 100, "notes": "Rich in product/company entities"},
            "overall": {"min": 75, "max": 95}
        },
        "notes": "Product description with concrete entities, features, and pricing"
    },
    
    {
        "id": "high_004",
        "name": "Step-by-step tutorial",
        "category": "high_quality",
        "chunk_heading": "Setting Up PostgreSQL Replication",
        "chunk_text": """This guide walks you through configuring master-slave replication in PostgreSQL 14 for high availability.

## Prerequisites

- Two Ubuntu 20.04 servers
- PostgreSQL 14 installed on both servers
- Sudo access on both machines
- Network connectivity between servers

## Step 1: Configure the Master Server

First, edit the PostgreSQL configuration file:

```bash
sudo nano /etc/postgresql/14/main/postgresql.conf
```

Add or modify these settings:
- `wal_level = replica`
- `max_wal_senders = 3`
- `wal_keep_segments = 64`
- `listen_addresses = '*'`

## Step 2: Set Up Replication User

Create a dedicated replication user:

```sql
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'strong_password_here';
```

## Step 3: Configure Host-Based Authentication

Edit pg_hba.conf to allow replication connections:

```bash
sudo nano /etc/postgresql/14/main/pg_hba.conf
```

Add this line:
```
host replication replicator slave_ip_address/32 md5
```

## Step 4: Restart Master and Create Base Backup

Restart PostgreSQL and create the base backup on the slave:

```bash
# On master
sudo systemctl restart postgresql

# On slave
pg_basebackup -h master_ip -D /var/lib/postgresql/14/main -U replicator -P -v -R -X stream -C -S pgstandby1
```

Your replication is now configured and running.""",
        "expected": {
            "query_answer": {"min": 80, "max": 100, "notes": "Complete tutorial with all steps"},
            "llm_rubric": {"min": 75, "max": 95, "notes": "Clear step-by-step structure"},
            "structure_quality": {"min": 80, "max": 100, "notes": "Excellent tutorial format"},
            "entity_focus": {"min": 70, "max": 90, "notes": "PostgreSQL-specific entities"},
            "overall": {"min": 75, "max": 95}
        },
        "notes": "Complete tutorial with prerequisites, steps, and code examples"
    },
    
    {
        "id": "high_005",
        "name": "Technical concept explanation",
        "category": "high_quality",
        "chunk_heading": "Understanding Vector Embeddings in Machine Learning",
        "chunk_text": """Vector embeddings are numerical representations of data that capture semantic meaning in a format that machines can process. By converting text, images, or other data types into dense vectors of floating-point numbers, embeddings enable AI systems to understand similarity and relationships.

## How Embeddings Work

When you input text into an embedding model like OpenAI's text-embedding-ada-002 or Google's Universal Sentence Encoder, the model transforms your text into a fixed-size vector (typically 384 to 1536 dimensions). Similar concepts produce vectors that are close together in the embedding space.

For example:
- "dog" and "puppy" would have similar embeddings
- "dog" and "automobile" would be far apart
- "king - man + woman" approximately equals "queen" (word arithmetic)

## Common Embedding Models

**OpenAI Embeddings**: text-embedding-ada-002 produces 1536-dimensional vectors. Excellent for general-purpose semantic search with strong performance across domains.

**Sentence Transformers**: Open-source models like all-MiniLM-L6-v2 create 384-dimensional embeddings. Faster and cheaper than proprietary options, ideal for resource-constrained applications.

**Cohere Embed**: Offers multilingual support with embed-multilingual-v2.0. Handles 100+ languages in a single model, producing 768-dimensional vectors.

## Applications in Production

1. **Semantic Search**: Find documents by meaning rather than keywords
2. **Recommendation Systems**: Suggest similar items based on embedding proximity
3. **Clustering**: Group related documents automatically
4. **Anomaly Detection**: Identify outliers in embedding space
5. **Cross-Modal Search**: Match images with text descriptions""",
        "expected": {
            "query_answer": {"min": 75, "max": 95, "notes": "Comprehensive concept explanation"},
            "llm_rubric": {"min": 75, "max": 95, "notes": "Well-organized educational content"},
            "structure_quality": {"min": 70, "max": 90, "notes": "Good sectioning and examples"},
            "entity_focus": {"min": 75, "max": 95, "notes": "Rich in ML/AI entities"},
            "overall": {"min": 75, "max": 95}
        },
        "notes": "Technical explanation with concrete examples and applications"
    }
]