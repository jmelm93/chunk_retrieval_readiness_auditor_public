"""Low quality test cases with major AI chunk retrieval barriers."""

LOW_QUALITY_CASES = [
    # Multiple vague cross-references breaking self-containment
    {
        "id": "low_v3_001",
        "name": "Content with multiple vague cross-references",
        "category": "low_quality",
        "chunk_heading": "Implementation Details",
        "chunk_text": """As discussed earlier in this guide, the approach outlined above requires careful consideration of the factors mentioned previously. The methodology described in the initial sections provides the foundation for understanding these concepts.

Following the framework established in the introduction, we can now apply the principles covered in the overview section. The techniques shown earlier demonstrate how to implement the strategies referenced throughout this documentation.

Building on the analysis presented above, the next steps involve utilizing the tools described in the previous chapter. This process leverages the concepts introduced at the beginning of our discussion and incorporates the best practices outlined in the preceding sections.

The configuration settings mentioned earlier should be adjusted according to the specifications detailed above. Remember to refer back to the installation guide provided in the first section and follow the troubleshooting steps described previously.

When implementing these changes, use the parameters defined in the setup section and apply the security measures outlined in the earlier chapters. The monitoring procedures covered above will help ensure that the system operates according to the guidelines established throughout this documentation.

As noted in the earlier sections, the performance optimizations discussed above can significantly improve results when combined with the techniques described previously. This approach builds upon the foundation established in the introductory material and extends the concepts covered in subsequent sections.""",
        "expected": {
            "query_answer": {"min": 20, "max": 40, "notes": "No useful information due to excessive vague references"},
            "llm_rubric": {"min": 15, "max": 35, "notes": "Extremely poor standalone quality"},
            "structure_quality": {"min": 25, "max": 45, "notes": "Basic paragraphs but no substance"},
            "entity_focus": {"min": 10, "max": 30, "notes": "No concrete entities or concepts"},
            "overall": {"min": 15, "max": 35}
        },
        "notes": "Extreme example of vague cross-references making content completely dependent on missing context"
    },

    # Misleading header with completely different content
    {
        "id": "low_v3_002",
        "name": "Advanced content under beginner heading",
        "category": "low_quality",
        "chunk_heading": "Getting Started with Programming",
        "chunk_text": """Quantum computing algorithms leverage superposition and entanglement phenomena to achieve exponential speedup over classical computation for specific problem domains including cryptography, optimization, and quantum simulation.

Variational Quantum Eigensolvers (VQE) utilize hybrid quantum-classical optimization to find ground state energies of molecular systems. The ansatz circuit preparation involves parameterized quantum gates with classical optimizer updating rotation angles based on expectation value measurements.

Grover's amplitude amplification algorithm provides quadratic speedup for unstructured search problems. The oracle function marks target states through phase rotation while diffusion operators perform inversion about average amplitude, requiring O(√N) iterations for N-element search spaces.

Quantum error correction schemes like surface codes protect logical qubits from decoherence through redundant encoding and syndrome measurement. Stabilizer formalism describes error syndromes using Pauli group generators while quantum error correction thresholds define maximum physical error rates for fault-tolerant computation.

Noisy Intermediate-Scale Quantum (NISQ) devices operate without full error correction, limiting coherent computation time and circuit depth. Quantum volume metrics characterize device capability through successful execution of random circuit sampling protocols.

Quantum machine learning algorithms including Quantum Approximate Optimization Algorithm (QAOA) and Quantum Neural Networks (QNN) explore potential quantum advantage for classification and optimization tasks, though classical simulation remains competitive for current problem sizes and device limitations.""",
        "expected": {
            "query_answer": {"min": 25, "max": 45, "notes": "Advanced quantum content under beginner heading"},
            "llm_rubric": {"min": 20, "max": 40, "notes": "Severe heading-content mismatch"},
            "structure_quality": {"min": 30, "max": 50, "notes": "Technical content poorly organized"},
            "entity_focus": {"min": 60, "max": 80, "notes": "Strong quantum computing entities but wrong context"},
            "overall": {"min": 25, "max": 45}
        },
        "notes": "Advanced quantum computing algorithms mislabeled as beginner programming content"
    },

    # Dense wall of text without structure or paragraph breaks
    {
        "id": "low_v3_003",
        "name": "Wall of text without formatting",
        "category": "low_quality",
        "chunk_heading": "Legal Contract Requirements",
        "chunk_text": """Contract formation requires mutual assent, consideration, capacity, and legality under common law principles, though specific requirements vary by jurisdiction and contract type, with commercial contracts governed by Uniform Commercial Code provisions in most US states while international agreements may invoke CISG or UNIDROIT principles depending on party domicile and choice of law provisions, and consideration must be legally sufficient though not necessarily adequate from economic perspective, meaning nominal consideration like one dollar can support binding agreements though courts may scrutinize transactions for unconscionability, duress, undue influence, or fraud, particularly in consumer contracts where disparity of bargaining power creates potential for exploitation, while capacity requirements exclude minors, mentally incompetent persons, and intoxicated individuals from binding agreement formation, though ratification upon reaching majority or regaining competency can validate previously voidable contracts, and legality requires both the subject matter and consideration to comply with applicable laws and public policy, so contracts for illegal activities like drug trafficking or prostitution are unenforceable, as are agreements that violate antitrust laws, employment discrimination statutes, or consumer protection regulations, while contract interpretation follows objective theory focusing on reasonable understanding of terms rather than subjective intent, using plain meaning rule for unambiguous language but allowing extrinsic evidence for ambiguous terms, with parol evidence rule limiting admission of prior negotiations or contemporaneous oral agreements that contradict written contract terms, though exceptions exist for fraud, mistake, or incomplete integration.""",
        "expected": {
            "query_answer": {"min": 30, "max": 50, "notes": "Legal information buried in dense text"},
            "llm_rubric": {"min": 15, "max": 35, "notes": "Extremely poor readability due to wall of text"},
            "structure_quality": {"min": 10, "max": 30, "notes": "No paragraph breaks or formatting"},
            "entity_focus": {"min": 50, "max": 70, "notes": "Many legal entities but incomprehensible structure"},
            "overall": {"min": 20, "max": 40}
        },
        "notes": "Legal contract content presented as single paragraph wall of text without formatting"
    },

    # Mixing completely unrelated concepts in one chunk
    {
        "id": "low_v3_004",
        "name": "Content mixing unrelated topics",
        "category": "low_quality",
        "chunk_heading": "Business Strategy Development",
        "chunk_text": """Strategic business planning involves market analysis and competitive positioning to achieve sustainable growth. Companies must evaluate internal capabilities while assessing external opportunities and threats in their operating environment.

Blockchain technology uses distributed ledger systems to record transactions across multiple nodes without centralized authority. Bitcoin's proof-of-work consensus mechanism requires significant computational energy, leading to environmental concerns about cryptocurrency mining operations.

The migration patterns of Arctic terns demonstrate remarkable navigation abilities, traveling roughly 44,000 miles annually between Arctic and Antarctic regions. These seabirds use magnetic field detection and celestial navigation to complete their intercontinental journeys.

Quantum entanglement occurs when particles become correlated in such a way that measuring one instantly affects the other, regardless of distance. Einstein called this "spooky action at a distance," though modern physics has confirmed the phenomenon through numerous experiments.

Effective marketing campaigns require clear value propositions and targeted messaging that resonates with specific customer segments. Social media platforms offer sophisticated targeting options based on demographics, interests, and behavioral patterns.

Photosynthesis converts light energy into chemical energy through complex biochemical reactions in chloroplasts. The light-dependent reactions produce ATP and NADPH, while the Calvin cycle uses these compounds to fix carbon dioxide into glucose molecules.

Customer retention strategies often prove more cost-effective than new customer acquisition, with existing customers showing higher lifetime value and referral potential.""",
        "expected": {
            "query_answer": {"min": 25, "max": 45, "notes": "Multiple unrelated topics prevent coherent contribution"},
            "llm_rubric": {"min": 15, "max": 35, "notes": "Severe topic confusion"},
            "structure_quality": {"min": 20, "max": 40, "notes": "No logical organization"},
            "entity_focus": {"min": 15, "max": 35, "notes": "Entities from completely different domains"},
            "overall": {"min": 20, "max": 40}
        },
        "notes": "Business strategy content mixed with blockchain, bird migration, quantum physics, and biology"
    },

    # Key information buried at the end
    {
        "id": "low_v3_005",
        "name": "Critical information buried at end",
        "category": "low_quality",
        "chunk_heading": "Medication Dosage Guidelines",
        "chunk_text": """Proper medication administration involves various considerations that healthcare providers must evaluate when prescribing treatments for patients. Many factors influence how medications work in different individuals, making personalized medicine an important aspect of modern healthcare.

The pharmaceutical industry continues to develop new treatments for various conditions, investing billions of dollars in research and development annually. Clinical trials follow strict protocols to ensure safety and efficacy before medications receive regulatory approval from agencies like the FDA.

Patient compliance remains a significant challenge in healthcare, with many individuals failing to take medications as prescribed. Educational programs and reminder systems help improve adherence rates, though socioeconomic factors also play important roles in medication access and compliance.

Different drug delivery methods offer various advantages and disadvantages. Oral medications provide convenience but may have slower onset times compared to intravenous administration. Topical preparations work well for localized conditions while avoiding systemic side effects.

Healthcare providers must consider drug interactions when prescribing multiple medications simultaneously. Some combinations can reduce effectiveness while others may increase toxicity risks. Regular monitoring helps identify potential problems before they become serious.

**Critical Dosing Information:**
Adults: Take 400mg twice daily with food. Maximum daily dose: 800mg. Children 6-12 years: 200mg twice daily. Children under 6: Consult pediatrician. Do not exceed recommended dose - overdose can cause liver damage or death. If dose is missed by more than 4 hours, skip and continue normal schedule. Seek immediate medical attention for symptoms including nausea, vomiting, confusion, or abdominal pain.""",
        "expected": {
            "query_answer": {"min": 30, "max": 50, "notes": "Critical dosing info buried at end"},
            "llm_rubric": {"min": 25, "max": 45, "notes": "Poor information hierarchy"},
            "structure_quality": {"min": 35, "max": 55, "notes": "Critical info formatting good but placement poor"},
            "entity_focus": {"min": 40, "max": 60, "notes": "Healthcare entities but unfocused until end"},
            "overall": {"min": 30, "max": 50}
        },
        "notes": "Medication content with critical dosing information buried at end after general pharmaceutical discussion"
    },

    # Academic jargon without clear explanations
    {
        "id": "low_v3_006",
        "name": "Academic content with excessive jargon",
        "category": "low_quality",
        "chunk_heading": "Machine Learning Model Optimization",
        "chunk_text": """Hyperparameter optimization employs metaheuristic algorithms to navigate high-dimensional configuration spaces, utilizing Bayesian optimization with Gaussian process priors and acquisition functions like expected improvement or upper confidence bounds to balance exploration-exploitation trade-offs during search processes.

Gradient-based optimization techniques leverage backpropagation through computational graphs to compute partial derivatives with respect to learnable parameters, enabling stochastic gradient descent variants including Adam, RMSprop, and Adagrad to adaptively adjust learning rates based on historical gradient statistics and momentum accumulation.

Regularization methodologies encompass L1 and L2 penalty terms that introduce sparsity-inducing or parameter-shrinking constraints into objective functions, while dropout mechanisms stochastically deactivate neural network units during training phases to mitigate overfitting phenomena through ensemble averaging effects.

Cross-validation frameworks partition datasets into training, validation, and test subsets using stratified sampling to preserve class distributions, with k-fold methodologies providing robust performance estimates through iterative holdout procedures that average metrics across multiple data splits.

Feature engineering encompasses dimensionality reduction techniques such as Principal Component Analysis (PCA), t-distributed Stochastic Neighbor Embedding (t-SNE), and Uniform Manifold Approximation and Projection (UMAP) that project high-dimensional representations into lower-dimensional manifolds while preserving relevant topological structures.

Ensemble methods including random forests, gradient boosting machines, and stacked generalization combine predictions from multiple weak learners through voting mechanisms or meta-learning approaches to achieve superior predictive performance compared to individual model architectures.""",
        "expected": {
            "query_answer": {"min": 35, "max": 55, "notes": "Technical content without clear explanations"},
            "llm_rubric": {"min": 20, "max": 40, "notes": "Excessive jargon without accessibility"},
            "structure_quality": {"min": 30, "max": 50, "notes": "Dense technical paragraphs"},
            "entity_focus": {"min": 65, "max": 85, "notes": "Strong ML entities but incomprehensible"},
            "overall": {"min": 30, "max": 50}
        },
        "notes": "Machine learning content with excessive academic jargon making it inaccessible"
    },

    # Multiple topics scattered without clear focus
    {
        "id": "low_v3_007",
        "name": "Scattered topics without focus",
        "category": "low_quality",
        "chunk_heading": "Technology Solutions",
        "chunk_text": """Modern technology offers numerous solutions for various challenges. Cloud computing provides scalable infrastructure for businesses of all sizes. Artificial intelligence enhances decision-making processes through data analysis and pattern recognition.

Renewable energy sources like solar and wind power help reduce carbon emissions while providing sustainable electricity generation. Battery storage technology improves grid stability and enables off-grid applications for remote locations.

Cybersecurity threats continue evolving as hackers develop sophisticated attack methods. Virtual private networks protect sensitive communications while firewalls block unauthorized network access. Employee training programs raise awareness about phishing attempts and social engineering tactics.

Mobile applications transform how people interact with services and information. User interface design principles improve accessibility and user experience across different platforms and devices. App store optimization helps developers reach target audiences more effectively.

Blockchain technology enables secure transactions without intermediary institutions. Smart contracts automate agreement execution based on predefined conditions. Cryptocurrency markets demonstrate high volatility requiring careful investment strategies and risk management approaches.

Internet of Things devices collect vast amounts of sensor data for analysis and automation. Edge computing reduces latency by processing information closer to data sources. Machine learning algorithms identify patterns in collected data to optimize operations and predict maintenance requirements.

These technological advances create opportunities for innovation while presenting new challenges for organizations adapting to digital transformation initiatives.""",
        "expected": {
            "query_answer": {"min": 25, "max": 45, "notes": "Multiple tech topics without depth"},
            "llm_rubric": {"min": 20, "max": 40, "notes": "Scattered focus across many topics"},
            "structure_quality": {"min": 35, "max": 55, "notes": "Basic structure but no coherence"},
            "entity_focus": {"min": 30, "max": 50, "notes": "Tech entities but scattered across domains"},
            "overall": {"min": 25, "max": 45}
        },
        "notes": "Technology content jumping between cloud, AI, renewable energy, cybersecurity, mobile, blockchain, IoT without focus"
    },

    # Legal document with run-on sentences and poor structure
    {
        "id": "low_v3_008",
        "name": "Legal content with poor sentence structure",
        "category": "low_quality",
        "chunk_heading": "Privacy Policy Terms",
        "chunk_text": """This privacy policy governs the collection, use, storage, and disclosure of personal information by our organization and its affiliated entities, subsidiaries, and third-party service providers in accordance with applicable privacy laws and regulations including but not limited to the General Data Protection Regulation (GDPR), California Consumer Privacy Act (CCPA), and other applicable local, state, federal, and international privacy legislation that may apply to users based on their geographic location and the nature of services provided, where personal information includes any information that can be used to identify an individual directly or indirectly including names, email addresses, phone numbers, mailing addresses, payment information, device identifiers, IP addresses, browsing history, location data, biometric information, and any other information collected through our websites, mobile applications, services, or interactions with our organization whether provided voluntarily by users or collected automatically through cookies, web beacons, analytics tools, or other tracking technologies that we may employ to improve user experience, analyze usage patterns, deliver personalized content, and conduct business operations including marketing, customer service, product development, and legal compliance activities that require processing of personal information for legitimate business purposes as defined by applicable law, though users may have certain rights regarding their personal information including the right to access, correct, delete, or restrict processing of their data subject to applicable legal requirements and business needs that may require retention of certain information for specific periods as mandated by law or necessary for protecting our legal interests in disputes or investigations.""",
        "expected": {
            "query_answer": {"min": 25, "max": 45, "notes": "Privacy policy info buried in run-on sentences"},
            "llm_rubric": {"min": 15, "max": 35, "notes": "Extremely poor readability"},
            "structure_quality": {"min": 10, "max": 30, "notes": "Single run-on paragraph"},
            "entity_focus": {"min": 45, "max": 65, "notes": "Privacy law entities but incomprehensible structure"},
            "overall": {"min": 20, "max": 40}
        },
        "notes": "Privacy policy content as single run-on sentence making it completely unreadable"
    },

    # Content with contradictory information
    {
        "id": "low_v3_009",
        "name": "Content with contradictory statements",
        "category": "low_quality",
        "chunk_heading": "Investment Risk Assessment",
        "chunk_text": """Investment risk assessment requires careful evaluation of potential losses and returns. Conservative investors should focus on low-risk investments that provide stable returns over time.

High-risk investments offer the best opportunities for significant wealth building. Aggressive trading strategies consistently outperform conservative approaches for long-term investors. Market timing allows skilled investors to maximize returns while minimizing losses.

Risk tolerance varies significantly among individuals based on age, income, and financial goals. Young investors can afford higher risk exposure due to longer time horizons for recovery from potential losses.

Conservative investment approaches minimize volatility and protect capital during market downturns. Government bonds and bank certificates of deposit provide guaranteed returns with no risk of principal loss. These safe investments should form the core of every portfolio.

Market volatility creates excellent buying opportunities for aggressive investors willing to accept short-term losses for long-term gains. Diversification across asset classes reduces overall portfolio risk while maintaining growth potential.

Risk assessment tools help investors understand their comfort level with potential losses. Conservative strategies work best for most investors, especially those approaching retirement who cannot recover from significant market downturns.

Professional financial advisors recommend aggressive growth strategies for building wealth quickly. Safe investments like bonds and CDs cannot keep pace with inflation and fail to build real wealth over time.""",
        "expected": {
            "query_answer": {"min": 25, "max": 45, "notes": "Contradictory investment advice"},
            "llm_rubric": {"min": 20, "max": 40, "notes": "Contradictory statements confuse readers"},
            "structure_quality": {"min": 35, "max": 55, "notes": "Basic structure but contradictory content"},
            "entity_focus": {"min": 40, "max": 60, "notes": "Investment entities but contradictory advice"},
            "overall": {"min": 25, "max": 45}
        },
        "notes": "Investment content with contradictory advice about conservative vs aggressive strategies"
    },

    # Stream of consciousness without clear structure
    {
        "id": "low_v3_010",
        "name": "Stream of consciousness content",
        "category": "low_quality",
        "chunk_heading": "Software Development Process",
        "chunk_text": """Writing code seems straightforward but actually involves many complex decisions that developers make throughout the process, and debugging can be really frustrating when you're trying to figure out why something isn't working as expected, which reminds me of the time I spent hours looking for a missing semicolon in JavaScript, though modern editors help catch these syntax errors much better than they used to, speaking of editors, there are so many choices now like VS Code, IntelliJ, Sublime Text, and others that each have their own advantages and disadvantages depending on what programming language you're using and what features you need, and version control with Git has revolutionized how teams collaborate on software projects, though merging conflicts can still be a pain to resolve when multiple developers modify the same files, which is why good communication and project management practices are so important, agile methodologies like Scrum help organize development sprints and keep everyone focused on deliverable goals, but sometimes the overhead of meetings and documentation can slow down actual coding time, and testing is crucial for maintaining code quality though it's often skipped when deadlines are tight, which leads to technical debt that accumulates over time and makes future changes more difficult and time-consuming, plus security considerations are becoming increasingly important as cyber threats continue to evolve and target software vulnerabilities.""",
        "expected": {
            "query_answer": {"min": 20, "max": 40, "notes": "Software dev info in stream of consciousness"},
            "llm_rubric": {"min": 15, "max": 35, "notes": "No clear structure or focus"},
            "structure_quality": {"min": 10, "max": 30, "notes": "Single run-on paragraph"},
            "entity_focus": {"min": 35, "max": 55, "notes": "Dev entities but scattered randomly"},
            "overall": {"min": 15, "max": 35}
        },
        "notes": "Software development content as stream of consciousness without structure"
    },

    # Content with multiple undefined acronyms and assumptions
    {
        "id": "low_v3_011",
        "name": "Content with undefined acronyms",
        "category": "low_quality",
        "chunk_heading": "Network Configuration Setup",
        "chunk_text": """Configure OSPF routing protocols within the BGP autonomous system ensuring proper LSA propagation across designated routers and backup designated routers in broadcast network segments. Implement MPLS traffic engineering with RSVP-TE signaling protocols to establish LSPs with specific bandwidth requirements and constraint-based routing calculations.

Deploy QoS policies using DSCP markings for traffic classification with strict priority queuing for voice traffic and weighted fair queuing for data applications. Configure PBR to redirect specific traffic flows through WAN optimization appliances before reaching MPLS provider edge routers.

Establish IPSec VPN tunnels using IKEv2 protocols with AES-256 encryption and SHA-256 hashing algorithms. Implement PSK authentication initially transitioning to PKI infrastructure with CRL validation and OCSP responder configuration for certificate revocation checking.

Configure HSRP or VRRP redundancy protocols on L3 switches with preemption enabled and track interface monitoring for automatic failover scenarios. Deploy LACP for port channel aggregation providing bandwidth scaling and link redundancy between distribution and access layer switches.

Implement 802.1X authentication with RADIUS AAA servers supporting dynamic VLAN assignment based on user credentials and device compliance policies. Configure MAB for IoT devices lacking 802.1X supplicant capabilities with predefined device fingerprinting rules.

Monitor network performance using SNMP MIBs with threshold-based alerting for interface utilization, CPU load, and memory consumption metrics. Deploy syslog centralization with severity-based filtering and correlation rules for proactive incident identification.""",
        "expected": {
            "query_answer": {"min": 30, "max": 50, "notes": "Network info but assumes technical background"},
            "llm_rubric": {"min": 20, "max": 40, "notes": "Excessive undefined acronyms"},
            "structure_quality": {"min": 25, "max": 45, "notes": "Technical structure but inaccessible"},
            "entity_focus": {"min": 60, "max": 80, "notes": "Strong network entities but undefined"},
            "overall": {"min": 25, "max": 45}
        },
        "notes": "Network configuration with excessive undefined acronyms making content inaccessible"
    },

    # Content jumping between time periods and topics randomly
    {
        "id": "low_v3_012",
        "name": "Content with random topic and time jumps",
        "category": "low_quality",
        "chunk_heading": "Historical Economic Development",
        "chunk_text": """The Industrial Revolution began in Britain during the 18th century, transforming manufacturing processes through mechanization and factory systems. Modern cryptocurrency markets exhibit extreme volatility requiring sophisticated risk management strategies for institutional investors.

Ancient Mesopotamian civilizations developed early banking systems using clay tablets to record transactions and loans. Today's federal reserve system manages monetary policy through interest rate adjustments and quantitative easing programs during economic downturns.

Medieval trade guilds controlled production and pricing within European cities, establishing quality standards and apprenticeship programs. Artificial intelligence algorithms now analyze market sentiment and execute high-frequency trading strategies in milliseconds.

The Great Depression of 1929 resulted from speculative bubbles and insufficient banking regulations, leading to widespread unemployment and economic hardship. Blockchain technology enables decentralized financial systems without traditional banking intermediaries.

Post-World War II economic expansion created middle-class prosperity in developed nations through increased consumer spending and suburban development. Climate change poses significant risks to global supply chains and agricultural production systems.

Roman currency systems unified trade across the Mediterranean basin using standardized coins and weights. Social media platforms influence consumer behavior and brand perception through targeted advertising and influencer marketing campaigns.

The development of double-entry bookkeeping during the Renaissance improved business accounting accuracy and enabled more complex commercial transactions across international markets.""",
        "expected": {
            "query_answer": {"min": 20, "max": 40, "notes": "Historical and modern topics randomly mixed"},
            "llm_rubric": {"min": 15, "max": 35, "notes": "No coherent timeline or focus"},
            "structure_quality": {"min": 30, "max": 50, "notes": "Basic paragraphs but no logical connection"},
            "entity_focus": {"min": 25, "max": 45, "notes": "Economic entities from different eras"},
            "overall": {"min": 20, "max": 40}
        },
        "notes": "Economic history content jumping randomly between ancient, medieval, modern, and contemporary topics"
    }
]