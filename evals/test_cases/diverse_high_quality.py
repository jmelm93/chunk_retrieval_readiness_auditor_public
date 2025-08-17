"""High quality test cases from diverse non-technical domains."""

DIVERSE_HIGH_QUALITY_CASES = [
    {
        "id": "diverse_high_001",
        "name": "Medical blood pressure guidelines",
        "category": "high_quality",
        "chunk_heading": "Managing Hypertension: Blood Pressure Guidelines and Treatment",
        "chunk_text": """Hypertension, or high blood pressure, affects nearly half of American adults and is a leading risk factor for heart disease and stroke. Understanding blood pressure readings and management strategies is crucial for preventing cardiovascular complications.

## Understanding Blood Pressure Readings

Blood pressure is measured in millimeters of mercury (mmHg) and recorded as two numbers:
- **Systolic pressure** (top number): Pressure when the heart beats
- **Diastolic pressure** (bottom number): Pressure when the heart rests between beats

### Current Classification Guidelines (American Heart Association 2023)

- **Normal**: Less than 120/80 mmHg
- **Elevated**: Systolic 120-129 and diastolic less than 80
- **Stage 1 Hypertension**: Systolic 130-139 or diastolic 80-89
- **Stage 2 Hypertension**: Systolic 140/90 mmHg or higher
- **Hypertensive Crisis**: Higher than 180/120 mmHg (requires immediate medical attention)

## Lifestyle Modifications for Blood Pressure Control

**DASH Diet**: The Dietary Approaches to Stop Hypertension diet can reduce systolic blood pressure by 8-14 mmHg. Focus on fruits, vegetables, whole grains, and lean proteins while limiting sodium to 2,300mg daily (ideally 1,500mg).

**Physical Activity**: Regular aerobic exercise (150 minutes moderate or 75 minutes vigorous weekly) can lower systolic pressure by 5-8 mmHg.

**Weight Management**: Losing 10 pounds can reduce systolic pressure by 5-20 mmHg. Target BMI between 18.5-24.9.

## Medication Options

First-line medications include ACE inhibitors (lisinopril, enalapril), ARBs (losartan, valsartan), calcium channel blockers (amlodipine), and thiazide diuretics (hydrochlorothiazide). Most patients require 2-3 medications for optimal control.""",
        "expected": {
            "query_answer": {"min": 80, "max": 100, "notes": "Comprehensive medical guidance"},
            "llm_rubric": {"min": 75, "max": 95, "notes": "Clear clinical information"},
            "structure_quality": {"min": 80, "max": 100, "notes": "Excellent medical formatting"},
            "entity_focus": {"min": 70, "max": 90, "notes": "Rich medical entities"},
            "overall": {"min": 75, "max": 95}
        },
        "notes": "High-quality medical content with specific measurements, medications, and guidelines"
    },
    
    {
        "id": "diverse_high_002",
        "name": "GDPR data rights explanation",
        "category": "high_quality",
        "chunk_heading": "GDPR Data Subject Rights: A Comprehensive Guide",
        "chunk_text": """The General Data Protection Regulation (GDPR) grants individuals eight fundamental rights regarding their personal data when interacting with organizations operating in the European Union.

## The Eight GDPR Rights

### 1. Right to be Informed (Articles 13-14)
Organizations must provide clear information about data collection, including:
- Identity and contact details of the data controller
- Purpose and legal basis for processing
- Data retention periods
- Recipients or categories of recipients

This information must be provided at the time of data collection in concise, transparent language.

### 2. Right of Access (Article 15)
Individuals can request confirmation whether their data is being processed and obtain a copy. Organizations must respond within one month, free of charge for the first request.

### 3. Right to Rectification (Article 16)
Data subjects can request correction of inaccurate personal data without undue delay. Organizations must also complete incomplete data when requested.

### 4. Right to Erasure/"Right to be Forgotten" (Article 17)
Individuals can request deletion when:
- Data is no longer necessary for original purpose
- Consent is withdrawn
- Data was unlawfully processed
- Erasure is required by law

### 5. Right to Restrict Processing (Article 18)
Processing can be restricted when accuracy is contested, processing is unlawful, or data is needed for legal claims.

## Implementation Requirements

Organizations must implement appropriate technical and organizational measures, maintain records of processing activities, and designate a Data Protection Officer (DPO) when required. Non-compliance can result in fines up to €20 million or 4% of global annual turnover, whichever is higher.""",
        "expected": {
            "query_answer": {"min": 80, "max": 100, "notes": "Complete legal requirements"},
            "llm_rubric": {"min": 75, "max": 95, "notes": "Clear legal explanations"},
            "structure_quality": {"min": 75, "max": 95, "notes": "Well-organized legal content"},
            "entity_focus": {"min": 70, "max": 90, "notes": "GDPR-specific terminology"},
            "overall": {"min": 75, "max": 95}
        },
        "notes": "Comprehensive legal content with specific articles, requirements, and penalties"
    },
    
    {
        "id": "diverse_high_003",
        "name": "Financial P/E ratio analysis",
        "category": "high_quality",
        "chunk_heading": "Understanding P/E Ratios in Stock Valuation",
        "chunk_text": """The Price-to-Earnings (P/E) ratio is a fundamental metric for evaluating stock valuations by comparing a company's share price to its earnings per share (EPS).

## Calculating P/E Ratio

**Formula**: P/E Ratio = Market Price per Share ÷ Earnings per Share (EPS)

Example: If Apple trades at $180 per share with EPS of $6.00:
P/E = $180 ÷ $6.00 = 30

This means investors pay $30 for every $1 of earnings.

## Types of P/E Ratios

**Trailing P/E**: Uses actual earnings from the last 12 months. Most reliable but backward-looking.

**Forward P/E**: Based on projected earnings. Useful for growth assessment but depends on estimate accuracy.

**PEG Ratio**: P/E divided by earnings growth rate. Accounts for growth, with PEG under 1.0 potentially indicating undervaluation.

## Interpreting P/E Ratios

**Industry Comparison**: Technology companies like Amazon (P/E ~60) typically have higher ratios than utilities like Southern Company (P/E ~20) due to growth expectations.

**Historical Context**: S&P 500 historical average is 15-16. Current levels above 25 may suggest overvaluation.

**Limitations**:
- Negative earnings make P/E meaningless
- Accounting differences affect comparability
- Doesn't consider debt levels or cash position
- One-time charges can distort earnings

## Sector Benchmarks (2024 Averages)

- Technology: 25-35
- Healthcare: 20-30
- Financial Services: 12-18
- Consumer Staples: 18-25
- Energy: 10-15

Always combine P/E analysis with other metrics like Price-to-Book, Debt-to-Equity, and Return on Equity for comprehensive valuation.""",
        "expected": {
            "query_answer": {"min": 75, "max": 95, "notes": "Complete financial concept"},
            "llm_rubric": {"min": 75, "max": 95, "notes": "Clear with examples"},
            "structure_quality": {"min": 75, "max": 95, "notes": "Well-structured financial content"},
            "entity_focus": {"min": 75, "max": 95, "notes": "Financial metrics and companies"},
            "overall": {"min": 75, "max": 95}
        },
        "notes": "Comprehensive financial education with formulas, examples, and sector comparisons"
    },
    
    {
        "id": "diverse_high_004",
        "name": "Educational Bloom's Taxonomy",
        "category": "high_quality",
        "chunk_heading": "Bloom's Taxonomy: Framework for Educational Objectives",
        "chunk_text": """Bloom's Taxonomy provides a hierarchical framework for categorizing educational learning objectives by complexity and specificity. Revised in 2001, it guides curriculum design, assessment creation, and instructional strategies.

## The Six Levels of Cognitive Learning

### 1. Remember (Knowledge)
**Definition**: Recall facts and basic concepts
**Action Verbs**: Define, list, memorize, name, state, match
**Example Activity**: Students list the capitals of European countries

### 2. Understand (Comprehension)  
**Definition**: Explain ideas or concepts
**Action Verbs**: Classify, describe, discuss, explain, summarize, paraphrase
**Example Activity**: Students explain the water cycle in their own words

### 3. Apply (Application)
**Definition**: Use information in new situations
**Action Verbs**: Execute, implement, solve, use, demonstrate, operate
**Example Activity**: Students use multiplication to calculate area of rectangles

### 4. Analyze (Analysis)
**Definition**: Draw connections among ideas
**Action Verbs**: Differentiate, organize, compare, contrast, examine, test
**Example Activity**: Students compare themes across different Shakespeare plays

### 5. Evaluate (Evaluation)
**Definition**: Justify a decision or course of action
**Action Verbs**: Appraise, argue, defend, judge, critique, support
**Example Activity**: Students evaluate which renewable energy source is best for their region

### 6. Create (Synthesis)
**Definition**: Produce original work
**Action Verbs**: Design, construct, develop, formulate, author, investigate
**Example Activity**: Students design a solution to reduce school cafeteria waste

## Implementation in Curriculum Design

Effective lessons should progress through multiple levels, starting with foundational knowledge and building toward higher-order thinking. Assessment questions should align with the intended cognitive level of learning objectives.""",
        "expected": {
            "query_answer": {"min": 80, "max": 100, "notes": "Complete educational framework"},
            "llm_rubric": {"min": 75, "max": 95, "notes": "Clear pedagogical content"},
            "structure_quality": {"min": 80, "max": 100, "notes": "Excellent hierarchical structure"},
            "entity_focus": {"min": 70, "max": 90, "notes": "Educational terminology"},
            "overall": {"min": 75, "max": 95}
        },
        "notes": "Comprehensive educational framework with definitions, examples, and applications"
    },
    
    {
        "id": "diverse_high_005",
        "name": "CRISPR gene editing explanation",
        "category": "high_quality",
        "chunk_heading": "CRISPR-Cas9: Precision Gene Editing Technology",
        "chunk_text": """CRISPR-Cas9 (Clustered Regularly Interspaced Short Palindromic Repeats) is a revolutionary gene-editing tool that allows scientists to make precise changes to DNA sequences in living cells.

## How CRISPR Works

The CRISPR system consists of two key components:

**Cas9 Enzyme**: Acts as molecular scissors that cut DNA at specific locations. The enzyme creates double-strand breaks in the DNA helix.

**Guide RNA (gRNA)**: A 20-nucleotide sequence that guides Cas9 to the target location by complementary base pairing. The gRNA includes a PAM (Protospacer Adjacent Motif) sequence necessary for Cas9 binding.

## The Gene Editing Process

1. **Design**: Scientists create a guide RNA matching the target DNA sequence
2. **Delivery**: CRISPR components are introduced into cells via viral vectors, electroporation, or microinjection
3. **Targeting**: Guide RNA leads Cas9 to the specific genomic location
4. **Cutting**: Cas9 creates a double-strand break at the target site
5. **Repair**: Cellular repair mechanisms fix the break through:
   - Non-Homologous End Joining (NHEJ): Often causes insertions/deletions
   - Homology-Directed Repair (HDR): Allows precise insertions using a DNA template

## Current Applications

**Medical Research**: Creating disease models, developing CAR-T cancer therapies, and studying gene function. Clinical trials target sickle cell disease, Leber congenital amaurosis, and transthyretin amyloidosis.

**Agriculture**: Developing drought-resistant crops, extending shelf life, and improving nutritional content. Examples include non-browning mushrooms and high-yield tomatoes.

**Biotechnology**: Producing biofuels, creating antimicrobial textiles, and engineering bacteria for environmental cleanup.

## Limitations and Challenges

Off-target effects occur when Cas9 cuts unintended sites. Delivery to specific tissues remains challenging. Ethical concerns surround germline editing and enhancement applications.""",
        "expected": {
            "query_answer": {"min": 75, "max": 95, "notes": "Complete scientific explanation"},
            "llm_rubric": {"min": 75, "max": 95, "notes": "Clear technical content"},
            "structure_quality": {"min": 75, "max": 95, "notes": "Well-organized scientific material"},
            "entity_focus": {"min": 80, "max": 100, "notes": "Rich scientific terminology"},
            "overall": {"min": 75, "max": 95}
        },
        "notes": "Comprehensive scientific content with mechanisms, applications, and technical details"
    },
    
    {
        "id": "diverse_high_006",
        "name": "French Revolution historical analysis",
        "category": "high_quality",
        "chunk_heading": "Causes of the French Revolution (1789-1799)",
        "chunk_text": """The French Revolution emerged from a complex interplay of social, economic, and political factors that destabilized the Ancien Régime and transformed France into a modern nation-state.

## Economic Crisis

France faced severe financial distress by the 1780s. The national debt reached 4 billion livres, with annual interest consuming 50% of state revenues. Contributing factors included:

- **Seven Years' War (1756-1763)**: Cost 1.3 billion livres
- **American Revolutionary War (1775-1783)**: Added 2 billion livres in debt
- **Tax System Inequality**: The First Estate (clergy) and Second Estate (nobility), who owned 40% of land, were exempt from most taxes

Finance ministers Jacques Turgot and Jacques Necker attempted reforms but faced aristocratic resistance through the Parlements.

## Social Tensions: The Three Estates

**First Estate** (1% of population): 130,000 clergy members controlling 10% of land and collecting tithes

**Second Estate** (2% of population): 350,000 nobles monopolizing military and government positions

**Third Estate** (97% of population): Included bourgeoisie, urban workers, and peasants bearing the tax burden. The bourgeoisie, despite wealth from trade and industry, lacked political power.

## Intellectual Movement: The Enlightenment

Philosophes challenged absolute monarchy and promoted reason:
- **Voltaire**: Advocated religious tolerance and freedom of speech
- **Montesquieu**: Proposed separation of powers in "The Spirit of Laws" (1748)
- **Rousseau**: Argued for popular sovereignty in "The Social Contract" (1762)

These ideas spread through salons, coffeehouses, and pamphlets, undermining royal authority.

## Immediate Triggers

The Assembly of Notables (1787) rejected tax reforms. Louis XVI convoked the Estates-General for May 5, 1789—the first meeting since 1614. The Third Estate's demands for voting by head rather than by estate led to the Tennis Court Oath (June 20, 1789) and formation of the National Assembly.""",
        "expected": {
            "query_answer": {"min": 80, "max": 100, "notes": "Comprehensive historical analysis"},
            "llm_rubric": {"min": 75, "max": 95, "notes": "Clear historical narrative"},
            "structure_quality": {"min": 75, "max": 95, "notes": "Well-organized historical content"},
            "entity_focus": {"min": 75, "max": 95, "notes": "Rich historical entities"},
            "overall": {"min": 75, "max": 95}
        },
        "notes": "Detailed historical analysis with dates, figures, and multiple causative factors"
    },
    
    {
        "id": "diverse_high_007",
        "name": "French cooking béchamel sauce",
        "category": "high_quality",
        "chunk_heading": "Mastering Béchamel: The Foundation of French Mother Sauces",
        "chunk_text": """Béchamel, one of the five French mother sauces, is a creamy white sauce that forms the base for countless classic dishes from lasagna to croque monsieur. Mastering this fundamental technique opens doors to sophisticated French cuisine.

## Essential Ingredients and Ratios

**Classic Ratio** (for 2 cups/500ml):
- 4 tablespoons (60g) unsalted butter
- 4 tablespoons (30g) all-purpose flour
- 2 cups (500ml) whole milk, warmed
- 1/4 teaspoon salt
- 1/8 teaspoon white pepper
- Pinch of nutmeg (traditional but optional)

## Step-by-Step Technique

### 1. Create the Roux
Melt butter in a heavy-bottomed saucepan over medium-low heat. Once foaming subsides, whisk in flour. Cook for 2-3 minutes, stirring constantly. The roux should bubble gently and smell slightly nutty but remain pale—no browning.

### 2. Add Milk Gradually
Remove pan from heat. Add milk in three additions, whisking vigorously after each to prevent lumps. The first addition will quickly thicken into a paste; subsequent additions will smooth the sauce.

### 3. Simmer and Season
Return to medium heat, whisking continuously until sauce thickens (5-7 minutes). It should coat the back of a spoon. Season with salt, white pepper, and nutmeg. For ultra-smooth results, strain through fine-mesh sieve.

## Consistency Variations

- **Light**: 1 tablespoon each butter/flour per cup milk (soups)
- **Medium**: 2 tablespoons each per cup (standard sauces)
- **Heavy**: 3 tablespoons each per cup (soufflé base)

## Classic Derivatives

**Mornay Sauce**: Add 1/2 cup grated Gruyère and 1/4 cup Parmesan
**Sauce Soubise**: Incorporate puréed onions cooked in butter
**Sauce Aurora**: Blend in 2 tablespoons tomato purée

## Troubleshooting

Lumps: Strain immediately or blend with immersion blender
Too thick: Whisk in warm milk gradually
Skin forming: Press plastic wrap directly on surface or dot with butter""",
        "expected": {
            "query_answer": {"min": 80, "max": 100, "notes": "Complete culinary instruction"},
            "llm_rubric": {"min": 75, "max": 95, "notes": "Clear cooking technique"},
            "structure_quality": {"min": 80, "max": 100, "notes": "Excellent recipe structure"},
            "entity_focus": {"min": 70, "max": 90, "notes": "Culinary terms and ingredients"},
            "overall": {"min": 75, "max": 95}
        },
        "notes": "Comprehensive cooking instruction with ratios, technique, variations, and troubleshooting"
    }
]