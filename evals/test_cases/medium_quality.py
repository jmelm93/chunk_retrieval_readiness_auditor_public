"""Medium quality test cases with some issues."""

MEDIUM_QUALITY_CASES = [
    {
        "id": "medium_001",
        "name": "Content with vague references",
        "category": "medium_quality",
        "chunk_heading": "Implementation Details",
        "chunk_text": """As mentioned in the previous section, the implementation requires careful consideration of several factors. The approach we discussed above provides the foundation for building this system.

The key components include:
- Data processing pipeline
- Storage mechanism  
- Retrieval interface
- Response generation

This builds on the architecture shown earlier and extends it with additional capabilities. The performance improvements over the previous version are significant, as we demonstrated in our benchmarks.

When implementing this solution, refer back to the configuration steps outlined previously. Those settings are critical for optimal performance.

The benefits of this approach include:
1. Better scalability than the old method
2. Improved accuracy compared to what we had before
3. Easier maintenance than the previous implementation

These advantages make it clear why this is the preferred solution, as explained in the introduction.""",
        "expected": {
            "query_answer": {"min": 40, "max": 60, "notes": "Vague references hurt self-containment"},
            "llm_rubric": {"min": 45, "max": 65, "notes": "Poor standalone quality"},
            "structure_quality": {"min": 60, "max": 80, "notes": "Structure OK but content vague"},
            "entity_focus": {"min": 30, "max": 50, "notes": "Too generic, lacks concrete entities"},
            "overall": {"min": 45, "max": 65}
        },
        "notes": "Multiple vague references ('as mentioned above', 'previous section') make it hard to understand standalone"
    },
    
    {
        "id": "medium_002", 
        "name": "Heading doesn't match content well",
        "category": "medium_quality",
        "chunk_heading": "Getting Started Guide",
        "chunk_text": """MongoDB uses a document-oriented data model that stores data in flexible, JSON-like documents. Unlike traditional relational databases, MongoDB doesn't require a predefined schema, allowing for more dynamic and evolving data structures.

Collections in MongoDB are analogous to tables in relational databases, but without enforcing a rigid structure. Each document within a collection can have different fields, and data types can vary between documents.

The query language in MongoDB is rich and expressive, supporting:
- Complex queries with multiple conditions
- Aggregation pipelines for data transformation
- Full-text search capabilities
- Geospatial queries for location-based data

Indexing in MongoDB is crucial for performance. You can create indexes on any field or combination of fields, including fields within embedded documents and arrays. MongoDB supports various index types including single field, compound, multikey, text, and geospatial indexes.

For high availability, MongoDB provides replica sets - a group of MongoDB instances that maintain the same data set. Replica sets provide redundancy and automatic failover, ensuring your application remains available even when servers fail.""",
        "expected": {
            "query_answer": {"min": 50, "max": 70, "notes": "Content good but doesn't match 'Getting Started'"},
            "llm_rubric": {"min": 55, "max": 75, "notes": "Misleading heading affects clarity"},
            "structure_quality": {"min": 60, "max": 80, "notes": "Well-structured content"},
            "entity_focus": {"min": 65, "max": 85, "notes": "Good MongoDB-specific entities"},
            "overall": {"min": 55, "max": 75}
        },
        "notes": "Heading promises 'Getting Started' but content is conceptual overview, not actionable steps"
    },
    
    {
        "id": "medium_003",
        "name": "Missing concrete entities",
        "category": "medium_quality",
        "chunk_heading": "Best Practices for System Design",
        "chunk_text": """When designing systems, it's important to follow established best practices that ensure scalability, reliability, and maintainability.

Start by understanding the requirements thoroughly. This includes both functional and non-functional requirements. Consider the expected load, data volume, and growth projections.

Design for scalability from the beginning. Even if you don't need it immediately, building scalability into your architecture early is much easier than retrofitting it later. Use proven patterns and approaches that have worked in similar scenarios.

Implement proper monitoring and logging throughout your system. You can't improve what you don't measure. Comprehensive monitoring helps identify bottlenecks and issues before they become critical problems.

Security should be built-in, not bolted-on. Consider security implications at every layer of your architecture. Use encryption for sensitive data, implement proper authentication and authorization, and follow the principle of least privilege.

Testing is crucial at all levels - unit tests, integration tests, and end-to-end tests. Automated testing ensures that changes don't break existing functionality and helps maintain code quality over time.

Documentation is often overlooked but critically important. Document your architecture decisions, API contracts, and operational procedures. Good documentation reduces onboarding time and helps teams work more effectively.""",
        "expected": {
            "query_answer": {"min": 55, "max": 75, "notes": "Generic advice, somewhat useful"},
            "llm_rubric": {"min": 50, "max": 70, "notes": "Very generic content"},
            "structure_quality": {"min": 65, "max": 85, "notes": "Clear paragraph structure"},
            "entity_focus": {"min": 20, "max": 40, "notes": "Almost no concrete entities"},
            "overall": {"min": 45, "max": 65}
        },
        "notes": "Generic best practices without specific tools, technologies, or concrete examples"
    },
    
    {
        "id": "medium_004",
        "name": "Wall of text without structure",
        "category": "medium_quality",
        "chunk_heading": "Machine Learning Model Deployment",
        "chunk_text": """Deploying machine learning models to production involves numerous considerations that go beyond simply training a model with good accuracy. You need to think about how the model will be served, whether through REST APIs, batch processing, or streaming pipelines, and each approach has its own trade-offs in terms of latency, throughput, and resource utilization. Model versioning is critical because you'll need to update models regularly as new data becomes available or performance degrades, and you must be able to roll back quickly if a new model performs poorly. Infrastructure choices matter significantly - you might use cloud services like AWS SageMaker, Google Cloud AI Platform, or Azure ML, or deploy on-premises using Kubernetes with tools like Kubeflow or Seldon Core, and the choice depends on your organization's requirements for data privacy, cost, and existing infrastructure. Monitoring in production is fundamentally different from development because you need to track not just model performance metrics but also data drift, prediction drift, and system metrics like latency and error rates, using tools like Prometheus, Grafana, or specialized ML monitoring platforms like Evidently AI or Whylabs. The model serving infrastructure needs to handle various concerns including authentication, rate limiting, caching of predictions when appropriate, and graceful degradation when the model is unavailable. Data preprocessing in production must exactly match what was done during training, which often means packaging preprocessing code with the model or maintaining separate preprocessing services that can introduce version mismatch issues if not carefully managed. Performance optimization might involve techniques like model quantization, pruning, or distillation to reduce model size and inference time, or using specialized hardware like GPUs or TPUs for inference, though this increases complexity and cost.""",
        "expected": {
            "query_answer": {"min": 50, "max": 70, "notes": "Good content but hard to scan"},
            "llm_rubric": {"min": 40, "max": 60, "notes": "Wall of text hurts readability"},
            "structure_quality": {"min": 20, "max": 40, "notes": "Poor structure - no breaks"},
            "entity_focus": {"min": 70, "max": 90, "notes": "Rich in ML/platform entities"},
            "overall": {"min": 45, "max": 65}
        },
        "notes": "Dense wall of text without paragraphs, lists, or other structural elements"
    },
    
    {
        "id": "medium_005",
        "name": "Generic heading with decent content",
        "category": "medium_quality",
        "chunk_heading": "Overview",
        "chunk_text": """Redis is an open-source, in-memory data structure store that can be used as a database, cache, and message broker. It supports various data structures including strings, hashes, lists, sets, sorted sets, bitmaps, hyperloglogs, and geospatial indexes.

## Performance Characteristics

Redis is known for exceptional performance, typically handling:
- 100,000+ operations per second on modest hardware
- Sub-millisecond latency for most operations
- Linear scalability with Redis Cluster

## Common Use Cases

**Session Storage**: Store user session data with automatic expiration using TTL (Time To Live) settings.

**Caching**: Reduce database load by caching frequently accessed data. Redis's LRU eviction policy automatically removes least-recently-used items when memory is full.

**Real-time Analytics**: Use sorted sets to maintain leaderboards, or hyperloglogs for unique visitor counting with minimal memory usage.

**Message Queuing**: Redis Pub/Sub provides simple message broadcasting, while Redis Streams offers more robust message queuing with consumer groups.

## Data Persistence Options

- **RDB Snapshots**: Point-in-time snapshots at specified intervals
- **AOF (Append Only File)**: Logs every write operation for better durability
- **Hybrid**: Combine both for optimal performance and data safety""",
        "expected": {
            "query_answer": {"min": 65, "max": 85, "notes": "Good content despite generic heading"},
            "llm_rubric": {"min": 60, "max": 80, "notes": "Generic heading hurts discoverability"},
            "structure_quality": {"min": 70, "max": 90, "notes": "Well-structured content"},
            "entity_focus": {"min": 75, "max": 95, "notes": "Strong Redis-specific entities"},
            "overall": {"min": 65, "max": 85}
        },
        "notes": "Generic 'Overview' heading doesn't indicate Redis content, but content itself is good"
    }
]