# Chunk Auditor - Advanced Content Retrieval Readiness Tool

## 🚀 Overview

Chunk Auditor is a comprehensive tool for evaluating web content's readiness for AI retrieval systems. It analyzes content chunks across multiple dimensions to help SEO teams optimize for LLM-powered search and chat interfaces.

### Key Features

- **Multi-dimensional scoring** across 5 evaluation criteria
- **Semantic chunking** with intelligent boundary detection
- **Content preprocessing** to remove navigation/footer noise
- **AI-powered entity extraction** during evaluation phase
- **Comprehensive reporting** in JSON and Markdown formats
- **Full text analysis** (no truncation in reports)

## 📊 Scoring Dimensions

| Dimension                     | Weight | Description                                           |
| ----------------------------- | ------ | ----------------------------------------------------- |
| **Query-Answer Completeness** | 25%    | How well chunks answer potential search queries       |
| **Entity Focus**              | 25%    | Topic coherence and entity concentration              |
| **LLM Rubric**                | 30%    | AI evaluation of standalone readability and structure |
| **Structure Quality**         | 20%    | HTML/Markdown structure and formatting                |

## 📦 Installation

```bash
# Clone the repository
git clone <repository_url>
cd chunk_retrieval_readiness_auditor_public

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (create .env file)
cat > .env << 'EOF'
OPENAI_API_KEY=sk-your-key-here
FIRECRAWL_API_KEY=fc-your-key-here  # Optional but recommended
VOYAGE_API_KEY=pa-your-key-here     # Optional, fallback to OpenAI
EOF
```

## 🎯 Usage

### Basic Commands

```bash
# Analyze a URL (recommended - uses Firecrawl for better extraction)
python main.py --url "https://example.com/article"

# Analyze a local file
python main.py --file "content.html" --format html

# Analyze direct content
python main.py --content "Your content here" --format markdown

# Run with sample content (for testing)
python main.py

# Enable debug output
python main.py --url "https://example.com" --debug
```

### Command Line Options

| Option            | Description                         | Default            |
| ----------------- | ----------------------------------- | ------------------ |
| `--url URL`       | URL to analyze                      | None               |
| `--file FILE`     | Local file to analyze               | None               |
| `--content TEXT`  | Direct content string               | None               |
| `--format FORMAT` | Content format (html/markdown/text) | html               |
| `--output DIR`    | Output directory                    | output             |
| `--config FILE`   | Custom config file                  | config/config.yaml |
| `--debug`         | Enable debug logging                | False              |
| `--skip-boundary` | Skip content boundary detection     | False              |

## 📁 Output Files

The tool generates three types of output files with timestamps:

### 1. JSON Report (`audit_domain_TIMESTAMP.json`)

- Complete chunk-by-chunk analysis
- All scores and sub-scores
- Entity extraction results
- Flags and recommendations
- Metadata and configuration

### 2. Markdown Report (`audit_domain_TIMESTAMP.md`)

- Human-readable format
- Executive summary with score distribution
- Detailed chunk analysis with full text
- Actionable recommendations
- Terminology guide

### 3. Summary Report (`audit_domain_TIMESTAMP_summary.txt`)

- Quick overview of results
- Top issues identified
- Chunks needing most attention
- Key metrics at a glance

## ⚙️ Configuration

Edit `config/config.yaml` to customize:

### Model Configuration

```yaml
models:
  default: "gpt-5-mini"
  overrides:
    content_preprocessing: "gpt-5-nano"
    query_answer: "gpt-5"
    llm_rubric: "gpt-4.1"
```

### Scoring Weights

Adjust the importance of each evaluation dimension:

```yaml
scoring:
  weights:
    query_answer: 0.30
    entity_focus: 0.25
    llm_rubric: 0.25
    structure_quality: 0.20
```

### Content Preprocessing

Control boundary detection for removing irrelevant content:

```yaml
content_preprocessing:
  enabled: true
  min_confidence: 3
  analysis_length: 10000
```

## 🏗️ Architecture

```
chunk_auditor/
├── config/              # Configuration management
│   ├── config.yaml      # Main configuration
│   └── config_handler.py # Config data classes
├── core/                # Core functionality
│   ├── document_loader.py # URL/file/content loading
│   └── pipeline.py      # Processing pipeline
├── evaluators/          # Scoring modules
│   ├── composite.py     # Orchestrates all evaluators
│   ├── query_answer.py  # Query completeness scoring
│   ├── llm_rubric.py    # LLM-based evaluation
│   └── structure_quality.py # HTML/structure analysis
├── extractors/          # Content extraction
│   └── content_boundary_analyzer.py # Remove nav/footer
├── reporting/           # Report generation
│   └── report_generator.py # JSON/Markdown/Summary
└── main.py             # Entry point
```

## 🔍 What Gets Analyzed

### For Each Chunk:

1. **Query-Answer Analysis**

   - Identifies likely search queries
   - Scores completeness (0-100)
   - Detects missing information
   - Evaluates standalone readability

2. **Entity Focus Analysis**

   - AI extracts and evaluates entities
   - Identifies concrete vs. generic entities
   - Calculates topic coherence
   - Measures entity diversity

3. **LLM Evaluation**

   - Standalone readability
   - Single topic focus
   - Structure clarity
   - Contextual completeness

4. **Structure Analysis**

   - Heading quality and hierarchy
   - List and formatting usage
   - Image alt text presence
   - HTML/Markdown semantics

5. **Size Optimization**
   - Token count analysis
   - Ideal range compliance
   - Split recommendations
   - Content density metrics

## 🚀 Advanced Features

### Content Boundary Detection

- AI-powered removal of navigation, footers, and boilerplate
- Configurable confidence thresholds
- Only applied to URL inputs (not direct content)
- Preserves main content integrity

### Semantic Chunking

- Uses LlamaIndex's SemanticSplitterNodeParser
- Respects natural content boundaries
- Fallback to sentence-based splitting
- Configurable chunk size and overlap

### Multi-Model Support

- Primary: Voyage AI embeddings (best performance)
- Fallback: OpenAI embeddings
- Configurable per evaluation type
- Graceful degradation without API keys

## 🐛 Troubleshooting

| Issue                 | Solution                                    |
| --------------------- | ------------------------------------------- |
| `ModuleNotFoundError` | Activate venv: `source venv/bin/activate`   |
| API Key Errors        | Check `.env` file and environment variables |
| Firecrawl Errors      | Check API key or use `--skip-boundary` flag |
| Large Content Timeout | Adjust `max_content_length` in config       |
| Memory Issues         | Reduce `batch_size` in config               |

## 📈 Interpreting Results

### Score Ranges

- **75-100** (Well Optimized): Ready for AI retrieval
- **60-74** (Needs Work): Some improvements recommended
- **0-59** (Poorly Optimized): Significant revision needed

### Chunk Type Recognition

The tool recognizes that different chunks serve different purposes:

- **Definition chunks**: Define key terms and concepts
- **Example chunks**: Provide concrete illustrations
- **Overview chunks**: Give high-level summaries
- **Detail chunks**: Deep dive into specifics
- **Bridge chunks**: Connect related concepts
- **Comparison chunks**: Compare and contrast items
- **Process chunks**: Describe step-by-step procedures
- **General chunks**: Mixed or uncategorized content (default)

Each type is evaluated appropriately - a definition chunk isn't penalized for not having examples, and an example chunk isn't penalized for not having comprehensive definitions.
