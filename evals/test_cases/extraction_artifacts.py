"""Test cases with extraction artifacts that should be ignored."""

EXTRACTION_ARTIFACT_CASES = [
    {
        "id": "artifact_001",
        "name": "Content with author byline and date",
        "category": "extraction_artifacts",
        "chunk_heading": "Understanding Kubernetes Pod Lifecycle",
        "chunk_text": """Understanding Kubernetes Pod Lifecycle

Written by Sarah Johnson
Published: March 15, 2024
Updated: March 20, 2024
5 min read

Kubernetes pods go through several phases during their lifecycle, from creation to termination. Understanding these phases is crucial for debugging and managing containerized applications effectively.

## Pod Phases

**Pending**: The pod has been accepted by the Kubernetes cluster, but one or more containers are not yet running. This includes time spent waiting for scheduling and downloading container images.

**Running**: The pod has been bound to a node, and all containers have been created. At least one container is running, starting, or restarting.

**Succeeded**: All containers in the pod have terminated successfully and will not be restarted. This typically happens for batch jobs.

**Failed**: All containers have terminated, and at least one container failed with a non-zero exit code or was terminated by the system.

**Unknown**: The state of the pod cannot be determined, typically due to communication errors with the node.

## Container States Within Pods

Each container within a pod can be in one of three states:
- **Waiting**: Container is not yet running (pulling image, applying secrets)
- **Running**: Container is executing without issues
- **Terminated**: Container has stopped execution

Understanding these states helps diagnose issues quickly and ensures smooth application deployment.""",
        "expected": {
            "query_answer": {"min": 70, "max": 90, "notes": "Good content despite metadata"},
            "llm_rubric": {"min": 70, "max": 90, "notes": "Should ignore author/date artifacts"},
            "structure_quality": {"min": 70, "max": 90, "notes": "Good structure, ignore metadata"},
            "entity_focus": {"min": 65, "max": 85, "notes": "Strong Kubernetes entities"},
            "overall": {"min": 70, "max": 90}
        },
        "notes": "Author byline and dates should be ignored - content itself is high quality"
    },
    
    {
        "id": "artifact_002",
        "name": "Social share buttons inline",
        "category": "extraction_artifacts",
        "chunk_heading": "Python Async/Await Best Practices",
        "chunk_text": """Python's async/await syntax provides powerful tools for writing concurrent code. Here are essential best practices for effective asynchronous programming.

Share this article: FacebookTwitterLinkedInRedditEmail

## Use asyncio.gather() for Concurrent Operations

When you need to run multiple async operations concurrently, use `asyncio.gather()` instead of awaiting them sequentially:

```python
# Good - concurrent execution
results = await asyncio.gather(
    fetch_user_data(user_id),
    fetch_order_history(user_id),
    fetch_preferences(user_id)
)

# Bad - sequential execution
user = await fetch_user_data(user_id)
orders = await fetch_order_history(user_id)
prefs = await fetch_preferences(user_id)
```

FacebookTwitterLinkedIn Share

## Avoid Blocking Operations

Never use blocking I/O operations in async functions. Use async alternatives:
- Replace `time.sleep()` with `await asyncio.sleep()`
- Use `aiohttp` instead of `requests`
- Use `aiofiles` for file operations

## Handle Exceptions Properly

Always handle exceptions in async code to prevent unhandled rejections:

```python
async def safe_fetch(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()
    except aiohttp.ClientError as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None
```

Tweet this Share on Facebook""",
        "expected": {
            "query_answer": {"min": 70, "max": 90, "notes": "Good technical content"},
            "llm_rubric": {"min": 65, "max": 85, "notes": "Should ignore social buttons"},
            "structure_quality": {"min": 70, "max": 90, "notes": "Good code examples"},
            "entity_focus": {"min": 60, "max": 80, "notes": "Python-specific entities"},
            "overall": {"min": 65, "max": 85}
        },
        "notes": "Social share button text should be ignored as extraction artifacts"
    },
    
    {
        "id": "artifact_003",
        "name": "Author bio with avatar description",
        "category": "extraction_artifacts",
        "chunk_heading": "GraphQL vs REST: Choosing the Right API Architecture",
        "chunk_text": """[Author avatar: Professional headshot of a person in business attire]

About the Author: Michael Chen is a Senior Software Architect with 15 years of experience in API design and distributed systems. Follow him on Twitter @mchen_dev.

GraphQL vs REST: Choosing the Right API Architecture

When building modern APIs, teams often debate between GraphQL and REST. Both have their strengths, and the choice depends on your specific use case.

## REST Advantages

**Simplicity**: REST's resource-based approach is intuitive and well-understood. Each endpoint represents a resource, making it easy to reason about.

**Caching**: HTTP caching works out-of-the-box with REST. CDNs and browsers can cache GET requests effectively.

**Tooling**: Mature ecosystem with extensive tooling for testing, documentation (OpenAPI/Swagger), and monitoring.

## GraphQL Advantages

**Flexible Queries**: Clients can request exactly what they need, reducing over-fetching and under-fetching problems.

**Single Endpoint**: All requests go through one endpoint, simplifying client implementation and API versioning.

**Type System**: Strong typing with schema definition provides excellent developer experience and auto-generated documentation.

## Decision Factors

Choose REST when:
- Building public APIs with unknown consumers
- Caching is critical for performance
- Team has limited GraphQL experience

Choose GraphQL when:
- Building complex, interconnected data models
- Mobile apps need bandwidth optimization
- Rapid frontend iteration is required

Written by Michael Chen | Last updated: January 2024""",
        "expected": {
            "query_answer": {"min": 75, "max": 95, "notes": "Comprehensive comparison"},
            "llm_rubric": {"min": 70, "max": 90, "notes": "Ignore author bio artifacts"},
            "structure_quality": {"min": 75, "max": 95, "notes": "Clear comparison structure"},
            "entity_focus": {"min": 70, "max": 90, "notes": "GraphQL and REST entities"},
            "overall": {"min": 70, "max": 90}
        },
        "notes": "Author bio and avatar description should be ignored - focus on technical content"
    },
    
    {
        "id": "artifact_004",
        "name": "Newsletter signup in middle",
        "category": "extraction_artifacts",
        "chunk_heading": "Docker Container Security Best Practices",
        "chunk_text": """Securing Docker containers is essential for protecting your applications and infrastructure. Here are critical security practices every team should implement.

## Use Official Base Images

Always start with official images from Docker Hub. These are regularly updated and maintained:

```dockerfile
# Good - official image
FROM node:18-alpine

# Risky - unknown source
FROM someuser/node:latest
```

📧 Want more DevOps tips? Subscribe to our newsletter!
[Email input field] [Subscribe button]
Join 10,000+ developers getting weekly insights

## Run as Non-Root User

Never run containers as root. Create and use a specific user:

```dockerfile
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
USER nodejs
```

## Scan Images for Vulnerabilities

Integrate vulnerability scanning into your CI/CD pipeline:
- Use `docker scan` or Trivy for local scanning
- Implement Snyk or Aqua Security for enterprise needs
- Set up automated scanning in your registry

Get our free security checklist! Enter your email below:
[Email field] [Download button]

## Limit Container Resources

Prevent resource exhaustion attacks by setting limits:

```yaml
resources:
  limits:
    memory: "256Mi"
    cpu: "500m"
  requests:
    memory: "128Mi"
    cpu: "250m"
```

## Use Read-Only Filesystems

When possible, run containers with read-only root filesystems:

```dockerfile
docker run --read-only --tmpfs /tmp myapp:latest
```""",
        "expected": {
            "query_answer": {"min": 70, "max": 90, "notes": "Good security practices"},
            "llm_rubric": {"min": 70, "max": 90, "notes": "Ignore newsletter CTAs"},
            "structure_quality": {"min": 70, "max": 90, "notes": "Good code examples"},
            "entity_focus": {"min": 65, "max": 85, "notes": "Docker-specific entities"},
            "overall": {"min": 70, "max": 90}
        },
        "notes": "Newsletter signup forms should be ignored as extraction artifacts"
    },
    
    {
        "id": "artifact_005",
        "name": "Navigation breadcrumbs with content",
        "category": "extraction_artifacts",
        "chunk_heading": "Redis Data Types Explained",
        "chunk_text": """Home > Documentation > Databases > NoSQL > Redis > Data Types

Redis Data Types Explained

View count: 12,543 | Reading time: 8 minutes
Last updated: February 28, 2024 by System Admin

[Print this page] [Export as PDF] [Share article]

Redis supports several data types that make it versatile for different use cases. Understanding these types is key to leveraging Redis effectively.

## Strings

The simplest Redis data type. Strings can contain any data including binary data, with a maximum size of 512MB.

```redis
SET user:1:name "John Doe"
GET user:1:name
```

You are here: Home > Documentation > Databases > NoSQL > Redis > Data Types > Strings

## Lists

Ordered collections of strings, implemented as linked lists. Perfect for queues and stacks.

```redis
LPUSH tasks "Send email"
RPUSH tasks "Generate report"
LRANGE tasks 0 -1
```

## Sets

Unordered collections of unique strings. Useful for tracking unique items.

```redis
SADD tags "python" "redis" "nosql"
SMEMBERS tags
```

## Sorted Sets

Sets where each member has an associated score, kept in sorted order.

```redis
ZADD leaderboard 100 "player1" 95 "player2"
ZRANGE leaderboard 0 -1 WITHSCORES
```

< Previous: Redis Installation | Next: Redis Commands >""",
        "expected": {
            "query_answer": {"min": 70, "max": 90, "notes": "Good Redis content"},
            "llm_rubric": {"min": 65, "max": 85, "notes": "Ignore navigation elements"},
            "structure_quality": {"min": 70, "max": 90, "notes": "Good code examples"},
            "entity_focus": {"min": 75, "max": 95, "notes": "Strong Redis entities"},
            "overall": {"min": 70, "max": 90}
        },
        "notes": "Navigation breadcrumbs and UI elements should be ignored"
    }
]