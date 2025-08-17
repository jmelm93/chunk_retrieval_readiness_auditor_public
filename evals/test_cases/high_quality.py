"""High quality test cases demonstrating perfect AI chunk retrieval readiness."""

HIGH_QUALITY_CASES = [
    # Technical documentation with specific implementation details
    {
        "id": "high_v3_001",
        "name": "Kubernetes Pod Scheduling with Resource Limits",
        "category": "high_quality",
        "chunk_heading": "Kubernetes Pod Scheduling with Resource Limits",
        "chunk_text": """Kubernetes Pod scheduling with resource limits ensures efficient cluster resource allocation by constraining CPU and memory usage per container. Resource requests guarantee minimum allocation, while limits prevent containers from exceeding specified thresholds.

**Resource Request Configuration**
Resource requests tell the scheduler the minimum CPU and memory a container needs to function properly. Set CPU requests in millicores (e.g., 100m = 0.1 CPU cores) and memory in bytes (e.g., 128Mi = 134MB).

```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

**Pod Quality of Service Classes**
Kubernetes assigns QoS classes based on resource configuration: Guaranteed (requests = limits), Burstable (requests < limits), and BestEffort (no limits set). Guaranteed pods receive highest scheduling priority and eviction protection.

**Scheduling Behavior**
The kube-scheduler evaluates node capacity against pod requests during placement decisions. Pods remain in Pending state when no nodes have sufficient resources to satisfy requests. Node pressure triggers eviction starting with BestEffort pods, followed by Burstable pods exceeding requests.

Proper resource configuration prevents resource contention, improves cluster stability, and enables predictable application performance across diverse workloads.""",
        "expected": {
            "query_answer": {"min": 85, "max": 100, "notes": "Specific implementation details with concrete examples"},
            "llm_rubric": {"min": 90, "max": 100, "notes": "Perfect standalone clarity with technical specifics"},
            "structure_quality": {"min": 85, "max": 100, "notes": "Excellent structure with code blocks and sections"},
            "entity_focus": {"min": 85, "max": 100, "notes": "High concentration of Kubernetes concepts"},
            "overall": {"min": 85, "max": 100}
        },
        "notes": "Perfect AI retrieval readiness: specific heading, front-loaded key facts, self-contained technical content"
    },
    
    # Product specifications with concrete details
    {
        "id": "high_v3_002", 
        "name": "MacBook Pro M3 Technical Specifications",
        "category": "high_quality",
        "chunk_heading": "MacBook Pro M3 Technical Specifications",
        "chunk_text": """The MacBook Pro M3 (14-inch, 2023) features Apple's M3 chip with 8-core CPU, 10-core GPU, and 16-core Neural Engine, delivering 20% faster performance than M2 while maintaining 22-hour battery life.

**Performance Specifications**
- **Processor**: M3 chip with 3nm process technology
- **Memory**: 8GB unified memory (configurable to 24GB)
- **Storage**: 512GB SSD (configurable up to 8TB)
- **Display**: 14.2-inch Liquid Retina XDR (3024×1964, 254 PPI)

**Connectivity and Ports**
Three Thunderbolt 4 ports support 40Gb/s data transfer and external display connectivity up to 6K resolution at 60Hz. HDMI 2.1 port enables 8K display output at 60Hz or 4K at 240Hz. MagSafe 3 charging supports fast charging up to 96W.

**Audio and Video Capabilities**
Six-speaker sound system with force-cancelling woofers provides studio-quality audio. 1080p FaceTime HD camera includes advanced image signal processor for improved low-light performance and Center Stage automatic framing.

**Physical Dimensions**
Weighs 3.5 pounds (1.6 kg) with dimensions 12.31 × 8.71 × 0.61 inches. Space Gray and Silver color options available. Backlit Magic Keyboard with Touch ID provides secure authentication and ambient light adjustment.

Starting price: $1,599 USD with educational discounts available for qualified students and educators.""",
        "expected": {
            "query_answer": {"min": 85, "max": 100, "notes": "Complete technical specifications with exact numbers"},
            "llm_rubric": {"min": 85, "max": 100, "notes": "Well-structured product information"},
            "structure_quality": {"min": 80, "max": 100, "notes": "Clear sections with bullet points"},
            "entity_focus": {"min": 85, "max": 100, "notes": "Strong focus on MacBook Pro specs"},
            "overall": {"min": 85, "max": 100}
        },
        "notes": "Perfect product specification chunk with specific numbers, clear structure, front-loaded key info"
    },

    # Financial analysis with specific data
    {
        "id": "high_v3_003",
        "name": "Tesla Q3 2024 Financial Performance Analysis", 
        "category": "high_quality",
        "chunk_heading": "Tesla Q3 2024 Financial Performance Analysis",
        "chunk_text": """Tesla reported Q3 2024 revenue of $25.18 billion, representing 8% year-over-year growth, with automotive gross margin improving to 19.3% from 16.9% in Q2 2024 due to production efficiency gains and cost reduction initiatives.

**Revenue Breakdown by Segment**
- **Automotive**: $20.02 billion (79.5% of total revenue)
- **Energy Generation and Storage**: $2.38 billion (+52% YoY)
- **Services and Other**: $2.79 billion (+29% YoY)

**Profitability Metrics**
Operating income reached $2.72 billion with operating margin of 10.8%, while net income totaled $2.17 billion ($0.62 per share). Free cash flow generated $2.74 billion, bringing year-to-date free cash flow to $7.53 billion.

**Vehicle Delivery Performance**
Tesla delivered 466,140 vehicles in Q3 2024, including 439,975 Model 3/Y and 26,165 Model S/X/Cybertruck. Production totaled 469,796 vehicles, maintaining delivery-production balance within 1% variance.

**Key Financial Ratios**
Return on equity increased to 19.3% from 17.1% in Q3 2023. Cash and investments balance of $29.94 billion provides substantial financial flexibility for capital expenditure programs and potential acquisitions.

The quarter demonstrated Tesla's operational maturity with sustained profitability across all business segments and strong cash generation supporting growth investments.""",
        "expected": {
            "query_answer": {"min": 85, "max": 100, "notes": "Comprehensive financial data with specific metrics"},
            "llm_rubric": {"min": 85, "max": 100, "notes": "Clear financial analysis structure"},
            "structure_quality": {"min": 85, "max": 100, "notes": "Well-organized sections with specific data"},
            "entity_focus": {"min": 85, "max": 100, "notes": "Strong focus on Tesla financial metrics"},
            "overall": {"min": 85, "max": 100}
        },
        "notes": "Excellent financial chunk with front-loaded key metrics, specific data, clear structure"
    },

    # Medical procedure with step-by-step instructions
    {
        "id": "high_v3_004",
        "name": "Blood Pressure Measurement Procedure",
        "category": "high_quality", 
        "chunk_heading": "Blood Pressure Measurement Procedure",
        "chunk_text": """Accurate blood pressure measurement requires proper cuff sizing, patient positioning, and technique to ensure readings within ±3 mmHg of true arterial pressure. Use cuff width covering 40% of upper arm circumference for adults.

**Patient Preparation Requirements**
Patient should sit quietly for 5 minutes before measurement with feet flat on floor, back supported, and arm at heart level. Avoid caffeine, exercise, or smoking for 30 minutes prior to measurement.

**Cuff Application Technique**
1. **Cuff Selection**: Choose appropriate size based on arm circumference (small adult: 22-26 cm, regular adult: 27-34 cm, large adult: 35-44 cm)
2. **Cuff Placement**: Position cuff 2-3 cm above antecubital fossa with inflation bladder centered over brachial artery
3. **Cuff Tightness**: Ensure snug fit allowing one finger insertion under cuff edge

**Measurement Protocol**
Inflate cuff to 30 mmHg above anticipated systolic pressure, then deflate at 2-3 mmHg per second. Record systolic pressure at first appearance of Korotkoff sounds (Phase I) and diastolic pressure at sound disappearance (Phase V).

**Quality Control Standards**
Take two measurements separated by 1-2 minutes and average results. If readings differ by >10 mmHg, obtain additional measurement. Document arm used, cuff size, and patient position for consistent follow-up measurements.

Normal adult blood pressure: <120/80 mmHg. Elevated: 120-129/<80 mmHg. Stage 1 hypertension: 130-139/80-89 mmHg.""",
        "expected": {
            "query_answer": {"min": 85, "max": 100, "notes": "Complete medical procedure with specific steps"},
            "llm_rubric": {"min": 85, "max": 100, "notes": "Clear medical instructions with exact specifications"},
            "structure_quality": {"min": 85, "max": 100, "notes": "Excellent step-by-step structure"},
            "entity_focus": {"min": 85, "max": 100, "notes": "Strong focus on blood pressure measurement"},
            "overall": {"min": 85, "max": 100}
        },
        "notes": "Perfect medical procedure chunk with specific measurements, clear steps, front-loaded key info"
    },

    # Software configuration with exact commands
    {
        "id": "high_v3_005",
        "name": "MySQL Database Connection Pool Configuration",
        "category": "high_quality",
        "chunk_heading": "MySQL Database Connection Pool Configuration", 
        "chunk_text": """MySQL connection pooling optimizes database performance by maintaining persistent connections, reducing connection overhead from 50-100ms per request to <1ms for pooled connections. Configure pool size based on concurrent user load and application requirements.

**Connection Pool Parameters**
```sql
[mysql]
max_connections = 200
innodb_buffer_pool_size = 2G
innodb_log_file_size = 512M
innodb_flush_log_at_trx_commit = 2
```

**Application-Level Pool Configuration**
Set minimum pool size to 5-10 connections for baseline availability and maximum pool size to 20-50 connections per application instance. Connection timeout should be 30 seconds with validation query "SELECT 1" executed every 60 seconds.

**HikariCP Java Configuration Example**
```java
HikariConfig config = new HikariConfig();
config.setJdbcUrl("jdbc:mysql://localhost:3306/database");
config.setMaximumPoolSize(20);
config.setMinimumIdle(5);
config.setConnectionTimeout(30000);
config.setIdleTimeout(600000);
```

**Performance Monitoring Metrics**
Monitor active connections, pool utilization percentage, and average connection wait time. High wait times (>100ms) indicate undersized pools, while consistently low utilization (<10%) suggests oversized configuration.

**Pool Size Calculation Formula**
Optimal pool size = ((core_count × 2) + effective_spindle_count). For typical web applications handling 1000 concurrent users, start with 20-25 connections per instance and adjust based on monitoring data.""",
        "expected": {
            "query_answer": {"min": 85, "max": 100, "notes": "Complete configuration guide with specific parameters"},
            "llm_rubric": {"min": 85, "max": 100, "notes": "Excellent technical documentation with code examples"},
            "structure_quality": {"min": 85, "max": 100, "notes": "Perfect structure with code blocks and formulas"},
            "entity_focus": {"min": 85, "max": 100, "notes": "Strong focus on MySQL connection pooling"},
            "overall": {"min": 85, "max": 100}
        },
        "notes": "Excellent technical chunk with specific configurations, code examples, performance metrics"
    },

    # Marketing strategy with specific metrics
    {
        "id": "high_v3_006",
        "name": "Email Marketing Campaign Performance Optimization",
        "category": "high_quality",
        "chunk_heading": "Email Marketing Campaign Performance Optimization",
        "chunk_text": """Email marketing campaign optimization focuses on improving open rates (target: 20-25%), click-through rates (target: 2-5%), and conversion rates (target: 1-3%) through strategic subject line testing, send time optimization, and audience segmentation.

**Subject Line Best Practices**
Limit subject lines to 41-50 characters for mobile optimization, with personalization increasing open rates by 26%. A/B testing reveals that questions outperform statements by 12%, while urgency words ("Limited", "Today only") improve performance by 8-15%.

**Send Time Optimization Strategy**
- **Tuesday-Thursday**: Peak engagement between 10 AM - 2 PM
- **Industry-specific timing**: B2B performs best Tuesday 10 AM, B2C shows higher engagement Saturday 8 AM - 10 AM
- **Time zone considerations**: Segment lists by geographic location for optimal delivery timing

**Audience Segmentation Approaches**
Demographic segmentation improves click-through rates by 14%, while behavioral segmentation (purchase history, website activity) increases conversion rates by 35%. Create segments based on engagement levels: active (opened/clicked last 30 days), inactive (30-90 days), and dormant (90+ days).

**Performance Metrics and Benchmarks**
Track delivery rate (>95%), bounce rate (<2%), unsubscribe rate (<0.5%), and spam complaint rate (<0.1%). List growth rate should maintain 15-25% annually through organic acquisition channels.

**Campaign Testing Framework**
Test one variable per campaign: subject line, send time, call-to-action placement, or email design. Minimum sample size of 1,000 recipients per variant ensures statistical significance with 95% confidence level.""",
        "expected": {
            "query_answer": {"min": 85, "max": 100, "notes": "Comprehensive email marketing guide with specific benchmarks"},
            "llm_rubric": {"min": 85, "max": 100, "notes": "Well-structured marketing strategy with data"},
            "structure_quality": {"min": 85, "max": 100, "notes": "Clear sections with specific metrics and bullets"},
            "entity_focus": {"min": 85, "max": 100, "notes": "Strong focus on email marketing optimization"},
            "overall": {"min": 85, "max": 100}
        },
        "notes": "Perfect marketing chunk with specific benchmarks, testing strategies, front-loaded key metrics"
    },

    # Cooking recipe with precise instructions
    {
        "id": "high_v3_007",
        "name": "French Onion Soup Preparation Method",
        "category": "high_quality", 
        "chunk_heading": "French Onion Soup Preparation Method",
        "chunk_text": """French onion soup preparation requires 45 minutes of slow caramelization at medium-low heat to develop deep flavor compounds, using 6 large yellow onions (3 pounds) thinly sliced and cooked in 4 tablespoons butter until deep amber brown.

**Onion Caramelization Process**
Heat butter in heavy-bottomed pot over medium-low heat (heat setting 3-4 out of 10). Add sliced onions with 1 teaspoon salt to draw moisture. Stir every 5-7 minutes, scraping browned bits from bottom. Total cooking time: 45-50 minutes until onions reach mahogany color.

**Broth Development Technique**
Deglaze caramelized onions with ½ cup dry white wine, scraping fond completely. Add 6 cups beef stock, 2 bay leaves, 1 teaspoon fresh thyme, and ½ teaspoon black pepper. Simmer 20 minutes to concentrate flavors.

**Cheese Topping Preparation**
- **Bread**: Use day-old French baguette slices, ½-inch thick, toasted until golden
- **Cheese**: Combine 1 cup grated Gruyère with ½ cup grated Parmesan for optimal melting
- **Assembly**: Float toasted bread on soup surface, top with cheese mixture

**Broiling Instructions**
Preheat broiler to high setting. Place oven-safe bowls on baking sheet 6 inches from heating element. Broil 2-3 minutes until cheese bubbles and develops golden-brown spots. Serve immediately while cheese remains molten.

Serves 6 portions. Total preparation time: 75 minutes (45 minutes caramelization + 30 minutes assembly/cooking).""",
        "expected": {
            "query_answer": {"min": 85, "max": 100, "notes": "Complete recipe with specific times and temperatures"},
            "llm_rubric": {"min": 85, "max": 100, "notes": "Clear cooking instructions with precise measurements"},
            "structure_quality": {"min": 85, "max": 100, "notes": "Excellent step-by-step structure"},
            "entity_focus": {"min": 85, "max": 100, "notes": "Strong focus on French onion soup preparation"},
            "overall": {"min": 85, "max": 100}
        },
        "notes": "Perfect recipe chunk with specific times, temperatures, measurements, clear structure"
    },

    # Legal compliance with specific requirements
    {
        "id": "high_v3_008",
        "name": "GDPR Data Retention Policy Requirements",
        "category": "high_quality",
        "chunk_heading": "GDPR Data Retention Policy Requirements", 
        "chunk_text": """GDPR Article 5(1)(e) mandates data retention periods that ensure personal data is kept only as long as necessary for specified processing purposes, with maximum storage periods varying by data type: customer records (6 years), marketing consent (3 years), and website analytics (26 months).

**Mandatory Retention Categories**
- **Financial Records**: 6 years minimum per tax legislation requirements
- **Employment Data**: 7 years post-termination for legal compliance
- **Customer Communications**: 3 years for contract dispute resolution
- **Marketing Consent**: Until withdrawal or 3 years of inactivity

**Data Subject Rights Implementation**
Organizations must respond to erasure requests within 30 days, except where legal obligations require longer retention. Document legitimate interests assessments for extended retention periods beyond standard business needs.

**Technical Implementation Requirements**
Implement automated deletion processes using data classification systems. Tag data with retention periods and deletion dates at collection point. Maintain deletion logs demonstrating compliance with retention schedules.

**Legal Basis Documentation**
Document specific legal basis for each retention period: contractual necessity, legal obligation, legitimate interests, or consent. Review retention schedules annually and update based on changing legal requirements or business needs.

**Compliance Monitoring Process**
Conduct quarterly audits of data retention practices. Monitor deletion processes for effectiveness and maintain records of data lifecycle management. Train data protection officers on retention policy enforcement and exception handling procedures.

Non-compliance penalties reach 4% of annual global turnover or €20 million, whichever is higher.""",
        "expected": {
            "query_answer": {"min": 85, "max": 100, "notes": "Comprehensive GDPR compliance guide with specific timelines"},
            "llm_rubric": {"min": 85, "max": 100, "notes": "Clear legal requirements with implementation details"},
            "structure_quality": {"min": 85, "max": 100, "notes": "Well-organized legal information with bullets"},
            "entity_focus": {"min": 85, "max": 100, "notes": "Strong focus on GDPR data retention"},
            "overall": {"min": 85, "max": 100}
        },
        "notes": "Excellent legal chunk with specific timeframes, compliance requirements, penalty information"
    },

    # Home improvement with specific steps and measurements
    {
        "id": "high_v3_009",
        "name": "Bathroom Tile Installation on Drywall Surfaces",
        "category": "high_quality",
        "chunk_heading": "Bathroom Tile Installation on Drywall Surfaces",
        "chunk_text": """Bathroom tile installation on drywall requires moisture barrier application and proper adhesive selection to prevent water damage, using cement-based adhesive rated for wet areas and 6 mil polyethylene vapor barrier behind tiling areas.

**Surface Preparation Requirements**
Clean drywall surface removing dust, grease, and loose paint. Apply primer-sealer to porous surfaces ensuring uniform absorption. Install cement backer board in high-moisture areas (shower surrounds) using 1¼-inch cement board screws every 8 inches.

**Moisture Protection System**
- **Vapor Barrier**: Install 6 mil polyethylene sheeting with 6-inch overlaps, sealed with construction tape
- **Waterproof Membrane**: Apply liquid membrane 2 coats minimum, extending 6 inches beyond tile area
- **Sealing**: Use silicone caulk (not grout) at all penetrations and corners

**Tile Layout and Installation**
Start installation from center point using chalk lines for reference. Apply adhesive with 3/16-inch notched trowel in 3-foot sections. Maintain consistent 1/16-inch grout lines using spacers. Check tile level every 3-4 tiles using 2-foot level.

**Grouting and Finishing Process**
Wait 24 hours before grouting. Apply grout diagonally using rubber float, removing excess immediately. Clean tile surface with damp sponge in circular motions. Apply grout sealer after 72-hour cure time.

**Quality Control Checkpoints**
Verify 95% adhesive coverage by lifting random tiles during installation. Test hollow spots by tapping tiles - solid sound indicates proper adhesion. Maintain room temperature 65-75°F during installation and 48-hour cure period.""",
        "expected": {
            "query_answer": {"min": 85, "max": 100, "notes": "Complete installation guide with specific measurements"},
            "llm_rubric": {"min": 85, "max": 100, "notes": "Clear DIY instructions with technical specifications"},
            "structure_quality": {"min": 85, "max": 100, "notes": "Excellent step-by-step structure with specific details"},
            "entity_focus": {"min": 85, "max": 100, "notes": "Strong focus on bathroom tile installation"},
            "overall": {"min": 85, "max": 100}
        },
        "notes": "Perfect DIY chunk with specific measurements, materials, step-by-step instructions"
    },

    # Investment strategy with specific allocation percentages
    {
        "id": "high_v3_010",
        "name": "Portfolio Asset Allocation for Retirement Planning",
        "category": "high_quality",
        "chunk_heading": "Portfolio Asset Allocation for Retirement Planning",
        "chunk_text": """Retirement portfolio asset allocation strategies balance growth potential with risk management, typically following age-based formulas where equity percentage equals 100 minus age (e.g., 40-year-old investor maintains 60% equity, 40% fixed income allocation).

**Target-Date Fund Allocation Model**
- **Age 25-35**: 90% equity (70% domestic, 20% international), 10% bonds
- **Age 36-50**: 80% equity (60% domestic, 20% international), 20% bonds  
- **Age 51-65**: 60% equity (45% domestic, 15% international), 40% bonds
- **Age 65+**: 40% equity (30% domestic, 10% international), 60% bonds/cash

**Risk-Adjusted Return Expectations**
Conservative allocation (30% equity): 4-6% annual return with 5-8% volatility. Moderate allocation (60% equity): 6-8% annual return with 10-12% volatility. Aggressive allocation (90% equity): 8-10% annual return with 15-18% volatility.

**Rebalancing Strategy Implementation**
Rebalance quarterly when asset class deviates >5% from target allocation. Use threshold rebalancing rather than calendar rebalancing for tax efficiency. Prioritize rebalancing within tax-advantaged accounts (401k, IRA) to minimize taxable events.

**International Diversification Benefits**
International equity exposure (20-30% of total equity) reduces portfolio correlation and provides currency diversification. Emerging market allocation (5-10% of total portfolio) offers growth potential but increases volatility.

**Implementation Through Low-Cost Vehicles**
Use index funds with expense ratios <0.20% to minimize fees. Total annual portfolio costs should not exceed 0.50% including advisory fees. Consider tax-loss harvesting in taxable accounts to improve after-tax returns by 0.5-1.0% annually.""",
        "expected": {
            "query_answer": {"min": 85, "max": 100, "notes": "Comprehensive investment strategy with specific allocations"},
            "llm_rubric": {"min": 85, "max": 100, "notes": "Clear financial planning with specific percentages"},
            "structure_quality": {"min": 85, "max": 100, "notes": "Well-organized with specific allocation breakdowns"},
            "entity_focus": {"min": 85, "max": 100, "notes": "Strong focus on retirement portfolio allocation"},
            "overall": {"min": 85, "max": 100}
        },
        "notes": "Excellent investment chunk with specific percentages, age-based guidelines, clear structure"
    },

    # Exercise instruction with specific sets and reps
    {
        "id": "high_v3_011",
        "name": "Progressive Overhead Press Training Protocol",
        "category": "high_quality",
        "chunk_heading": "Progressive Overhead Press Training Protocol",
        "chunk_text": """Progressive overhead press training builds shoulder strength and stability through systematic load progression, starting with 65-70% of one-rep max for 3 sets of 5 repetitions, increasing weight by 2.5-5 pounds weekly while maintaining proper form mechanics.

**Starting Weight Calculation**
Determine one-rep maximum through testing or estimation (bodyweight × 0.75 for untrained males, × 0.5 for females). Begin training program with 65% of 1RM, allowing proper form development and neuromuscular adaptation.

**Weekly Progression Schedule**
- **Week 1-2**: 3 sets × 5 reps at 65% 1RM
- **Week 3-4**: 3 sets × 5 reps at 70% 1RM  
- **Week 5-6**: 3 sets × 3 reps at 75% 1RM
- **Week 7-8**: 3 sets × 3 reps at 80% 1RM

**Proper Form Mechanics**
Stand with feet shoulder-width apart, core braced, and barbell positioned at shoulder level. Press weight directly overhead following straight vertical path. Avoid excessive back arch by maintaining neutral spine position throughout movement.

**Accessory Exercise Integration**
Include lateral raises (3×12), face pulls (3×15), and pike push-ups (3×8) twice weekly to strengthen supporting musculature. Rotator cuff strengthening prevents impingement during overhead movements.

**Recovery and Adaptation Protocols**
Allow 48-72 hours between overhead pressing sessions for muscle protein synthesis and strength adaptation. Deload every 4th week by reducing intensity to 50-60% 1RM while maintaining movement patterns.

**Performance Benchmarks**
Intermediate strength standards: 1.25× bodyweight for males, 0.75× bodyweight for females. Advanced standards: 1.5× bodyweight for males, 1.0× bodyweight for females.""",
        "expected": {
            "query_answer": {"min": 85, "max": 100, "notes": "Complete training protocol with specific progression"},
            "llm_rubric": {"min": 85, "max": 100, "notes": "Clear exercise instructions with specific sets/reps"},
            "structure_quality": {"min": 85, "max": 100, "notes": "Excellent progression structure with specific percentages"},
            "entity_focus": {"min": 85, "max": 100, "notes": "Strong focus on overhead press training"},
            "overall": {"min": 85, "max": 100}
        },
        "notes": "Perfect exercise chunk with specific progression, form cues, performance benchmarks"
    },

    # Cybersecurity implementation with specific tools
    {
        "id": "high_v3_012",
        "name": "Multi-Factor Authentication Implementation Strategy",
        "category": "high_quality",
        "chunk_heading": "Multi-Factor Authentication Implementation Strategy",
        "chunk_text": """Multi-factor authentication (MFA) implementation reduces account compromise risk by 99.9% according to Microsoft security research, using time-based one-time passwords (TOTP), SMS backup, and hardware security keys for comprehensive protection against credential-based attacks.

**MFA Method Security Rankings**
1. **Hardware Security Keys** (FIDO2/WebAuthn): Phishing-resistant, 99.9% effective
2. **Authenticator Apps** (Google Authenticator, Authy): 96-98% effective against attacks
3. **SMS/Voice Calls**: 76-84% effective, vulnerable to SIM swapping
4. **Email-based codes**: 65-75% effective, weakest option

**Implementation Priority Framework**
Deploy MFA for high-risk accounts first: administrative access, financial systems, customer data repositories. Require hardware keys for privileged accounts and TOTP for standard user accounts. Implement backup authentication methods for account recovery scenarios.

**Technical Deployment Considerations**
Integrate MFA with existing identity providers (Active Directory, Okta, Azure AD) using SAML 2.0 or OAuth 2.0 protocols. Configure session timeout policies: 8 hours for standard users, 4 hours for administrative access, immediate timeout for high-risk actions.

**User Experience Optimization**
Enable "remember device" functionality for 30 days on trusted devices. Provide clear setup instructions with QR codes for authenticator app enrollment. Implement progressive authentication requiring additional factors only for sensitive operations.

**Monitoring and Compliance Metrics**
Track MFA enrollment rates (target: 98% within 90 days), authentication success rates (>95%), and bypass request frequency (<2% monthly). Monitor for authentication anomalies: unusual locations, device types, or failed attempt patterns.

**Emergency Access Procedures**
Maintain break-glass administrative accounts with alternative authentication methods. Store backup codes in secure password managers with offline access capabilities.""",
        "expected": {
            "query_answer": {"min": 85, "max": 100, "notes": "Comprehensive MFA implementation with specific effectiveness rates"},
            "llm_rubric": {"min": 85, "max": 100, "notes": "Clear security implementation strategy"},
            "structure_quality": {"min": 85, "max": 100, "notes": "Well-organized with priority rankings and metrics"},
            "entity_focus": {"min": 85, "max": 100, "notes": "Strong focus on MFA implementation"},
            "overall": {"min": 85, "max": 100}
        },
        "notes": "Excellent security chunk with specific effectiveness data, implementation priorities, clear metrics"
    }
]