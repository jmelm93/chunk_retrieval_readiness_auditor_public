"""Medium quality test cases with moderate AI chunk retrieval barriers."""

MEDIUM_QUALITY_CASES = [
    # Generic heading with good content but not front-loaded
    {
        "id": "medium_v3_001",
        "name": "Cloud security best practices with generic heading",
        "category": "medium_quality",
        "chunk_heading": "Best Practices",
        "chunk_text": """Modern cloud environments present unique security challenges that require comprehensive protection strategies. Organizations must balance accessibility with security requirements while maintaining operational efficiency.

When implementing cloud security measures, it's important to understand the shared responsibility model. Cloud providers secure the infrastructure, while customers secure their applications and data. This division creates potential gaps if not properly managed.

**Key Security Measures**
Multi-factor authentication should be mandatory for all administrative accounts, with hardware security keys preferred for highest-risk users. Network segmentation using virtual private clouds (VPCs) provides isolation between different application environments.

**Data Protection Requirements**
Encryption at rest protects stored data using AES-256 encryption standards. Transport layer security (TLS 1.3) secures data in transit between services and users. Regular key rotation every 90 days ensures cryptographic material remains secure.

**Monitoring and Compliance**
Centralized logging aggregates security events from all cloud resources for analysis. Security Information and Event Management (SIEM) tools process log data to identify potential threats. Automated compliance scanning validates configurations against industry standards like SOC 2 and ISO 27001.

Regular security assessments and penetration testing identify vulnerabilities before malicious actors exploit them. Incident response procedures should include cloud-specific escalation paths and containment strategies.

The investment in comprehensive cloud security typically reduces security incidents by 60-80% while improving regulatory compliance posture.""",
        "expected": {
            "query_answer": {"min": 65, "max": 80, "notes": "Good content but generic heading hurts discoverability"},
            "llm_rubric": {"min": 60, "max": 75, "notes": "Generic heading affects usability"},
            "structure_quality": {"min": 70, "max": 85, "notes": "Well-structured but lacks specificity in title"},
            "entity_focus": {"min": 70, "max": 85, "notes": "Strong cloud security entities"},
            "overall": {"min": 65, "max": 80}
        },
        "notes": "Good cloud security content hampered by generic 'Best Practices' heading"
    },

    # Vague cross-references affecting self-containment
    {
        "id": "medium_v3_002",
        "name": "Content with occasional vague references",
        "category": "medium_quality", 
        "chunk_heading": "React Component State Management",
        "chunk_text": """React component state management controls how data flows through application interfaces, enabling dynamic user interactions and responsive user experiences.

**Local State Implementation**
The useState hook manages component-level state for simple data like form inputs, toggle states, and temporary UI conditions. As mentioned in previous sections, useState returns a state variable and setter function for updates.

```javascript
const [count, setCount] = useState(0);
const [isVisible, setIsVisible] = useState(true);
```

**State Update Patterns**
State updates are asynchronous and may be batched for performance optimization. When updating state based on previous values, use functional updates to ensure accuracy. This approach prevents race conditions that occur with direct state mutation.

```javascript
// Correct functional update
setCount(prevCount => prevCount + 1);

// Avoid direct mutation
setCount(count + 1); // May be stale
```

**Complex State Management**
For complex state objects, consider useReducer for predictable state transitions. The reducer pattern centralizes state logic and makes debugging easier through clear action types.

**Performance Considerations**
Minimize unnecessary re-renders by memoizing child components with React.memo() and optimizing state structure. Group related state variables together and separate unrelated state to reduce update frequency.

React DevTools provides excellent debugging capabilities for tracking state changes and component re-render patterns during development.""",
        "expected": {
            "query_answer": {"min": 65, "max": 80, "notes": "Good React content with minor reference issues"},
            "llm_rubric": {"min": 60, "max": 75, "notes": "Vague reference affects standalone quality"},
            "structure_quality": {"min": 75, "max": 90, "notes": "Good structure with code examples"},
            "entity_focus": {"min": 75, "max": 90, "notes": "Strong React concept focus"},
            "overall": {"min": 65, "max": 80}
        },
        "notes": "React state management content with vague reference to 'previous sections'"
    },

    # Important information not front-loaded
    {
        "id": "medium_v3_003",
        "name": "Key information buried in middle",
        "category": "medium_quality",
        "chunk_heading": "Diabetes Blood Sugar Management",
        "chunk_text": """Managing blood sugar levels effectively requires understanding how different factors influence glucose throughout the day. Many people struggle with consistent monitoring and adjustment strategies.

Daily blood sugar fluctuations occur naturally due to meal timing, physical activity, stress levels, and sleep quality. These variations are normal but should remain within target ranges for optimal health outcomes.

**Monitoring Frequency Guidelines**
Regular glucose testing provides data for treatment adjustments and pattern recognition. Testing schedules vary based on treatment type and individual risk factors.

**Critical Target Ranges for Adults**
Fasting blood glucose should measure 80-130 mg/dL (4.4-7.2 mmol/L) upon waking. Post-meal readings taken 2 hours after eating should remain below 180 mg/dL (10.0 mmol/L). Hemoglobin A1C levels should stay under 7% for most adults, though individualized targets may vary.

**Lifestyle Management Strategies**
Consistent meal timing helps stabilize glucose patterns throughout the day. Carbohydrate counting allows for precise insulin dosing when using intensive management protocols. Regular physical activity improves insulin sensitivity and glucose uptake by muscle tissues.

**Emergency Response Protocols**
Hypoglycemia symptoms include shakiness, sweating, confusion, and rapid heartbeat. Treat with 15 grams fast-acting carbohydrates (glucose tablets, fruit juice) and retest blood sugar after 15 minutes.

Healthcare provider consultation is essential for developing personalized management plans and adjusting medications based on blood sugar trends and lifestyle factors.""",
        "expected": {
            "query_answer": {"min": 65, "max": 80, "notes": "Good medical content but key info not front-loaded"},
            "llm_rubric": {"min": 60, "max": 75, "notes": "Important ranges buried in middle section"},
            "structure_quality": {"min": 70, "max": 85, "notes": "Good organization but key info placement issues"},
            "entity_focus": {"min": 70, "max": 85, "notes": "Strong diabetes management focus"},
            "overall": {"min": 65, "max": 80}
        },
        "notes": "Diabetes management content with critical target ranges not in opening paragraph"
    },

    # Minor topic drift within same domain
    {
        "id": "medium_v3_004",
        "name": "Content with minor topic drift",
        "category": "medium_quality",
        "chunk_heading": "Home Solar Panel Installation",
        "chunk_text": """Solar panel installation for residential properties involves electrical work, structural assessment, and permit acquisition to ensure safe and compliant energy generation systems.

**Electrical System Requirements**
Most residential installations require electrical panel upgrades to handle solar input. Install dedicated disconnect switches and production meters for safety and monitoring. Grid-tie inverters convert DC power to AC power compatible with household appliances.

**Roof Structural Assessment**
Professional roof inspection evaluates load-bearing capacity and identifies optimal panel placement. South-facing roof sections with minimal shading provide maximum energy production. Roof age and material condition affect installation feasibility and long-term performance.

**Permit and Inspection Process**
Building permits ensure installations meet local electrical and structural codes. Many jurisdictions require licensed electrician involvement for grid connection work. Utility interconnection agreements specify net metering terms and power export limitations.

Speaking of energy efficiency, upgrading home insulation and windows often provides better return on investment than solar panels alone. Energy audits identify air leaks and efficiency improvements that reduce overall energy consumption.

**Financial Considerations and Incentives**
Federal tax credits cover 30% of installation costs through 2032, with gradual reduction thereafter. State and local incentives vary significantly by location. Financing options include solar loans, leases, and power purchase agreements with different ownership structures.

Installation typically takes 1-3 days depending on system size and complexity. Most residential systems range from 4-10 kW capacity generating 6,000-15,000 kWh annually based on location and weather patterns.""",
        "expected": {
            "query_answer": {"min": 65, "max": 80, "notes": "Good solar content with minor drift to insulation topic"},
            "llm_rubric": {"min": 60, "max": 75, "notes": "Topic drift affects focus quality"},
            "structure_quality": {"min": 70, "max": 85, "notes": "Good structure but topic consistency issues"},
            "entity_focus": {"min": 65, "max": 80, "notes": "Mostly solar entities with some drift"},
            "overall": {"min": 65, "max": 80}
        },
        "notes": "Solar panel content with brief drift to home insulation topic"
    },

    # Basic structure that could use more formatting
    {
        "id": "medium_v3_005",
        "name": "Content with basic structure needing formatting",
        "category": "medium_quality",
        "chunk_heading": "Personal Finance Budget Creation",
        "chunk_text": """Creating a personal budget helps track income and expenses while building toward financial goals. The 50/30/20 rule provides a simple framework for allocating money across different spending categories.

This budgeting approach designates 50% of after-tax income for essential expenses like housing, utilities, groceries, and minimum debt payments. Housing costs including rent or mortgage payments should not exceed 28% of gross monthly income according to financial planning guidelines.

The 30% category covers discretionary spending on dining out, entertainment, hobbies, and non-essential purchases. This allocation allows lifestyle flexibility while maintaining financial discipline. Tracking discretionary expenses often reveals surprising spending patterns and opportunities for optimization.

Twenty percent goes toward financial goals including emergency fund contributions, retirement savings, and debt repayment beyond minimums. Building an emergency fund with 3-6 months of expenses provides financial security during unexpected events like job loss or medical emergencies.

Budgeting tools range from simple spreadsheets to comprehensive apps like Mint, YNAB, or Personal Capital. Manual tracking using notebooks or spreadsheets works well for people who prefer hands-on budget management. Automated tools link bank accounts and categorize transactions automatically but require initial setup time.

Regular budget reviews identify spending trends and highlight areas needing adjustment. Monthly budget meetings with household members ensure everyone understands financial priorities and goals. Quarterly reviews allow for larger adjustments based on income changes or life events.

The key to successful budgeting is consistency and gradual improvement rather than perfection from the start.""",
        "expected": {
            "query_answer": {"min": 65, "max": 80, "notes": "Good budget content but could use better formatting"},
            "llm_rubric": {"min": 60, "max": 75, "notes": "Basic structure lacks emphasis and bullets"},
            "structure_quality": {"min": 55, "max": 70, "notes": "Plain paragraphs without formatting enhancement"},
            "entity_focus": {"min": 70, "max": 85, "notes": "Strong budgeting concept focus"},
            "overall": {"min": 60, "max": 75}
        },
        "notes": "Personal finance content with basic structure that would benefit from bullet points and formatting"
    },

    # Somewhat generic header for specific content
    {
        "id": "medium_v3_006",
        "name": "Specific content under generic header",
        "category": "medium_quality",
        "chunk_heading": "Getting Started",
        "chunk_text": """Docker containerization streamlines application deployment by packaging software with dependencies into portable, lightweight containers that run consistently across different environments.

**Container Image Creation**
Dockerfile defines container build instructions using layered approach for efficiency. Base images like Alpine Linux (5MB) or Ubuntu (28MB) provide minimal operating system functionality. Each instruction creates a new layer, so combining commands reduces image size.

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

**Docker Compose for Multi-Service Applications**
Docker Compose orchestrates multiple containers using YAML configuration files. Define services, networks, and volumes declaratively for consistent development and testing environments.

**Container Resource Management**
Set memory limits (--memory=512m) and CPU constraints (--cpus=1.5) to prevent containers from consuming excessive system resources. Monitor container performance using docker stats command for resource utilization metrics.

**Registry and Distribution**
Docker Hub provides public image registry for sharing containerized applications. Private registries like Amazon ECR or Azure Container Registry secure proprietary applications. Image versioning using semantic tags (v1.2.3) enables controlled deployments.

**Security Best Practices**
Run containers as non-root users when possible to minimize security risks. Scan images for vulnerabilities using tools like Clair or Snyk. Keep base images updated with latest security patches through automated rebuild pipelines.""",
        "expected": {
            "query_answer": {"min": 65, "max": 80, "notes": "Good Docker content under generic heading"},
            "llm_rubric": {"min": 60, "max": 75, "notes": "Generic 'Getting Started' doesn't indicate Docker content"},
            "structure_quality": {"min": 75, "max": 90, "notes": "Good technical structure with code examples"},
            "entity_focus": {"min": 75, "max": 90, "notes": "Strong Docker-specific entities"},
            "overall": {"min": 65, "max": 80}
        },
        "notes": "Comprehensive Docker content hindered by generic 'Getting Started' heading"
    },

    # Good content with occasional unclear pronouns
    {
        "id": "medium_v3_007",
        "name": "Content with unclear pronoun references",
        "category": "medium_quality",
        "chunk_heading": "Weight Loss Nutrition Strategies",
        "chunk_text": """Sustainable weight loss requires creating a caloric deficit of 500-750 calories daily through combination of dietary changes and increased physical activity, leading to 1-2 pounds of weight loss per week.

**Macronutrient Balance for Weight Loss**
Protein intake should target 0.8-1.2 grams per kilogram of body weight to preserve muscle mass during weight loss. This nutrient increases satiety and has higher thermic effect than carbohydrates or fats, requiring more energy for digestion and metabolism.

**Meal Timing and Frequency**
Research shows meal timing has minimal impact on weight loss compared to total caloric intake. Some people find success with intermittent fasting approaches, while others prefer smaller, frequent meals. The approach depends on individual preferences and lifestyle factors.

**Food Quality and Nutrient Density**
Prioritize whole foods like vegetables, lean proteins, whole grains, and fruits over processed alternatives. These provide greater satiety and nutritional value per calorie. Fiber-rich foods promote fullness and support digestive health during caloric restriction.

**Hydration and Weight Management**
Drinking water before meals can increase satiety and reduce caloric intake by 10-15%. Sometimes thirst masquerades as hunger, leading to unnecessary snacking. It also supports metabolic processes and helps maintain energy levels during dietary changes.

**Behavioral Strategies**
Food logging increases awareness of eating patterns and portion sizes. Mindful eating practices help distinguish between physical hunger and emotional triggers. Creating supportive environments removes tempting foods from easy access while stocking healthy alternatives.""",
        "expected": {
            "query_answer": {"min": 65, "max": 80, "notes": "Good nutrition content with some unclear references"},
            "llm_rubric": {"min": 60, "max": 75, "notes": "Pronoun clarity issues affect readability"},
            "structure_quality": {"min": 70, "max": 85, "notes": "Good structure with clear sections"},
            "entity_focus": {"min": 70, "max": 85, "notes": "Strong weight loss nutrition focus"},
            "overall": {"min": 65, "max": 80}
        },
        "notes": "Weight loss content with unclear pronoun references ('this nutrient', 'the approach', 'it')"
    },

    # Missing key context that would help standalone understanding
    {
        "id": "medium_v3_008",
        "name": "Content missing introductory context",
        "category": "medium_quality",
        "chunk_heading": "API Rate Limiting Implementation",
        "chunk_text": """Rate limiting algorithms control API request frequency to prevent service abuse and ensure fair resource allocation among users. Token bucket and sliding window algorithms provide different approaches to request throttling.

**Token Bucket Algorithm Implementation**
This method maintains a bucket with fixed capacity that refills at constant rate. Each request consumes one token, and requests are rejected when bucket is empty. Bucket size determines burst capacity while refill rate sets sustained throughput.

```python
class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
    
    def allow_request(self):
        self._refill()
        if self.tokens > 0:
            self.tokens -= 1
            return True
        return False
```

**Sliding Window Rate Limiting**
Sliding window counters track requests within moving time periods for more accurate rate limiting. Implementation requires distributed storage like Redis for multi-server deployments.

**HTTP Response Headers**
Include rate limit headers in API responses: X-RateLimit-Limit (total allowed), X-RateLimit-Remaining (requests left), and X-RateLimit-Reset (reset time). These headers help clients implement proper retry logic.

**Error Handling and User Experience**
Return HTTP 429 status code when rate limits are exceeded. Provide clear error messages indicating when clients can retry requests. Implement exponential backoff in client SDKs to reduce server load during rate limiting events.""",
        "expected": {
            "query_answer": {"min": 65, "max": 80, "notes": "Good API content but assumes some technical background"},
            "llm_rubric": {"min": 60, "max": 75, "notes": "Missing context about what APIs are"},
            "structure_quality": {"min": 75, "max": 90, "notes": "Good technical structure with code examples"},
            "entity_focus": {"min": 75, "max": 90, "notes": "Strong API rate limiting focus"},
            "overall": {"min": 65, "max": 80}
        },
        "notes": "API rate limiting content that could benefit from brief API context for general audiences"
    },

    # Content mixing related but distinct concepts
    {
        "id": "medium_v3_009",
        "name": "Content mixing related concepts",
        "category": "medium_quality",
        "chunk_heading": "Small Business Marketing Fundamentals",
        "chunk_text": """Small business marketing requires strategic approach balancing limited budgets with maximum reach and impact. Digital marketing channels often provide better return on investment than traditional advertising methods.

**Social Media Marketing Strategy**
Facebook and Instagram advertising allows precise demographic targeting with budgets starting at $5 daily. Create engaging content showcasing products and customer testimonials. Post consistently 3-5 times weekly to maintain audience engagement.

**Search Engine Optimization Basics**
Local SEO helps businesses appear in "near me" searches and Google My Business listings. Optimize website content with local keywords and maintain consistent business information across online directories.

**Email Marketing for Customer Retention**
Email campaigns cost approximately $0.02 per recipient and generate average ROI of $42 per dollar spent. Collect customer emails at point of sale and through website opt-ins. Newsletter content should provide value beyond promotional messages.

**Networking and Community Involvement**
Joining local business associations and chamber of commerce creates referral opportunities. Speaking at community events establishes expertise and builds brand recognition. These relationships often generate more qualified leads than online advertising.

**Customer Service as Marketing Tool**
Excellent customer service generates word-of-mouth referrals and positive online reviews. Respond to online reviews professionally and quickly to demonstrate commitment to customer satisfaction. Happy customers typically refer 2-3 new customers annually.

**Budget Allocation Guidelines**
Allocate 7-10% of gross revenue to marketing activities for growth-stage businesses. Track marketing spend per acquisition channel to identify most cost-effective strategies for future investment.""",
        "expected": {
            "query_answer": {"min": 65, "max": 80, "notes": "Good marketing content covering multiple channels"},
            "llm_rubric": {"min": 60, "max": 75, "notes": "Covers many topics without deep focus"},
            "structure_quality": {"min": 70, "max": 85, "notes": "Good organization but broad scope"},
            "entity_focus": {"min": 65, "max": 80, "notes": "Marketing terms but scattered across channels"},
            "overall": {"min": 65, "max": 80}
        },
        "notes": "Small business marketing content covering multiple channels without focusing deeply on any one"
    },

    # Good technical content with slightly vague terminology
    {
        "id": "medium_v3_010",
        "name": "Technical content with vague terminology",
        "category": "medium_quality",
        "chunk_heading": "Database Index Performance Optimization",
        "chunk_text": """Database index optimization improves query performance by reducing data scan operations and enabling efficient record retrieval. Proper index design can improve query performance by 10-100x depending on data volume and query patterns.

**Index Type Selection**
B-tree indexes work well for equality and range queries on ordered data. Hash indexes optimize exact match lookups but don't support range operations. Bitmap indexes are effective for low-cardinality columns with many repeated values.

**Composite Index Design**
Multi-column indexes should order columns by selectivity and query patterns. Place most selective columns first in composite indexes. This approach maximizes index effectiveness for various query combinations.

**Index Maintenance Considerations**
Indexes require storage space and maintenance overhead during data modifications. Each additional index slows INSERT, UPDATE, and DELETE operations. Monitor index usage statistics to identify unused indexes consuming resources unnecessarily.

**Query Execution Plan Analysis**
Database query planners use cost-based optimization to select execution strategies. Review execution plans to identify full table scans that might benefit from indexing. Look for high-cost operations and excessive row processing in query plans.

**Performance Monitoring Metrics**
Track query response times, index hit ratios, and disk I/O patterns to evaluate optimization effectiveness. Many database systems provide built-in performance monitoring tools for index analysis.

Consider partitioning strategies for very large tables to improve query performance and index maintenance efficiency. Partitioning works best when queries frequently filter on partition key columns.""",
        "expected": {
            "query_answer": {"min": 65, "max": 80, "notes": "Good database content with some vague terms"},
            "llm_rubric": {"min": 60, "max": 75, "notes": "Some vague terminology affects clarity"},
            "structure_quality": {"min": 70, "max": 85, "notes": "Good technical structure"},
            "entity_focus": {"min": 70, "max": 85, "notes": "Strong database optimization focus"},
            "overall": {"min": 65, "max": 80}
        },
        "notes": "Database optimization content with vague terms like 'this approach' and 'many database systems'"
    },

    # Content with good information placement but generic conclusion
    {
        "id": "medium_v3_011",
        "name": "Content with generic conclusion",
        "category": "medium_quality",
        "chunk_heading": "Home Security System Installation Guide",
        "chunk_text": """Professional home security system installation typically costs $300-800 depending on system complexity, with DIY installation reducing costs by 60-70% while requiring 4-6 hours for complete setup.

**System Component Planning**
Door and window sensors protect primary entry points using magnetic contacts that trigger when opened. Motion detectors cover interior spaces with 30-foot detection range and pet-immune options for households with animals under 40 pounds.

**Control Panel Placement Strategy**
Install main control panel near primary entrance but hidden from window view to prevent tampering. Location should have reliable cellular or WiFi connectivity for monitoring service communication. Backup battery provides 24-48 hours of operation during power outages.

**Sensor Installation Specifications**
Mount door sensors within ¾ inch gap between magnet and switch for reliable operation. Place window sensors on opening sash rather than frame to prevent false alarms from vibration. Motion detectors work best in corners 6-8 feet high with clear sight lines.

**Monitoring Service Integration**
Professional monitoring services cost $15-50 monthly and provide 24/7 response to alarm triggers. Self-monitoring options using smartphone apps eliminate monthly fees but require homeowner availability for alarm response.

**Testing and Maintenance Protocols**
Test all sensors monthly by triggering each zone individually. Replace backup batteries annually or when low-battery alerts activate. Clean detector lenses quarterly to maintain sensitivity and reduce false alarms.

Overall, proper planning and installation ensures reliable home protection and peace of mind for families.""",
        "expected": {
            "query_answer": {"min": 65, "max": 80, "notes": "Good installation guide with generic ending"},
            "llm_rubric": {"min": 60, "max": 75, "notes": "Generic conclusion weakens specificity"},
            "structure_quality": {"min": 75, "max": 90, "notes": "Good technical structure throughout"},
            "entity_focus": {"min": 75, "max": 90, "notes": "Strong home security focus"},
            "overall": {"min": 65, "max": 80}
        },
        "notes": "Home security installation guide with good specifics but generic concluding paragraph"
    },

    # Content with good structure but missing key implementation details
    {
        "id": "medium_v3_012",
        "name": "Content missing implementation details",
        "category": "medium_quality",
        "chunk_heading": "Kubernetes Horizontal Pod Autoscaling",
        "chunk_text": """Horizontal Pod Autoscaling (HPA) automatically adjusts the number of pod replicas based on CPU utilization, memory usage, or custom metrics to maintain application performance during varying load conditions.

**HPA Configuration Requirements**
Enable metrics server in Kubernetes cluster to collect resource utilization data. Define resource requests in pod specifications as HPA uses these values to calculate scaling decisions. Set minimum and maximum replica counts to prevent over-scaling or under-scaling scenarios.

**Scaling Metrics and Thresholds**
CPU utilization target of 70% provides good balance between performance and resource efficiency. Memory-based scaling requires careful tuning as memory usage patterns differ from CPU patterns. Custom metrics like request queue length or response time offer application-specific scaling triggers.

**Scaling Behavior Configuration**
HPA evaluates metrics every 15 seconds by default but only scales up after 3 minutes of sustained high utilization. Scale-down operations wait 5 minutes to prevent rapid scaling fluctuations. Configure these intervals based on application startup time and load patterns.

**Advanced HPA Features**
Multiple metrics can be combined using different policies: average, maximum, or custom algorithms. Behavior policies control scaling velocity and prevent excessive pod creation during traffic spikes.

**Monitoring and Troubleshooting**
Monitor HPA events and decisions using kubectl describe hpa command. Common issues include missing metrics, insufficient resource requests, or applications that don't scale horizontally effectively.

Proper HPA configuration reduces manual intervention while maintaining consistent application performance across different traffic patterns.""",
        "expected": {
            "query_answer": {"min": 65, "max": 80, "notes": "Good HPA content but missing specific implementation examples"},
            "llm_rubric": {"min": 60, "max": 75, "notes": "Missing concrete configuration examples"},
            "structure_quality": {"min": 70, "max": 85, "notes": "Good structure but could use YAML examples"},
            "entity_focus": {"min": 75, "max": 90, "notes": "Strong Kubernetes HPA focus"},
            "overall": {"min": 65, "max": 80}
        },
        "notes": "Kubernetes HPA content with good concepts but missing specific YAML configuration examples"
    }
]