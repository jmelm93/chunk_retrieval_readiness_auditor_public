"""Test cases with extraction artifacts from diverse non-technical domains."""

DIVERSE_EXTRACTION_ARTIFACT_CASES = [
    {
        "id": "diverse_artifact_001",
        "name": "News article with journalist byline",
        "category": "extraction_artifacts",
        "chunk_heading": "Federal Reserve Signals Potential Rate Changes",
        "chunk_text": """Federal Reserve Signals Potential Rate Changes

By Jennifer Martinez, Economics Correspondent
Published: March 28, 2024 at 9:45 AM EST
Updated: March 28, 2024 at 2:15 PM EST
📧 Email this article | 🐦 Tweet | 📘 Share on Facebook

The Federal Reserve indicated Wednesday that interest rate adjustments may come sooner than previously anticipated, citing recent inflation data and employment trends that suggest a shifting economic landscape.

Fed Chair Jerome Powell emphasized during the press conference that the central bank remains "data-dependent" in its approach. The latest Consumer Price Index showed a 3.2% year-over-year increase, down from 3.5% the previous month but still above the Fed's 2% target.

## Key Economic Indicators

The unemployment rate stands at 3.8%, near historical lows, while wage growth has moderated to 4.1% annually. These figures suggest a labor market that remains tight but is gradually cooling from pandemic-era extremes.

"We're seeing progress toward our dual mandate of price stability and maximum employment," Powell stated. "However, we remain vigilant about potential risks to the economic outlook."

Financial markets responded positively, with the S&P 500 gaining 1.2% following the announcement. Bond yields fell as investors adjusted expectations for future rate moves.

## Impact on Consumers

For consumers, potential rate changes could affect:
- Mortgage rates, currently averaging 6.8% for 30-year fixed loans
- Credit card APRs, which typically adjust within 1-2 billing cycles
- Savings account yields, expected to remain elevated near 4.5%
- Auto loan rates, currently averaging 7.2% for new vehicles

Jennifer Martinez has covered economics and Federal Reserve policy for 15 years. Follow her @JMartinezEcon""",
        "expected": {
            "query_answer": {"min": 70, "max": 90, "notes": "Good economic content"},
            "llm_rubric": {"min": 70, "max": 90, "notes": "Should ignore byline"},
            "structure_quality": {"min": 70, "max": 90, "notes": "Well-structured article"},
            "entity_focus": {"min": 65, "max": 85, "notes": "Fed, Powell, economic data"},
            "overall": {"min": 70, "max": 90}
        },
        "notes": "Quality news content with journalist byline, timestamps, and social sharing buttons"
    },
    
    {
        "id": "diverse_artifact_002",
        "name": "Academic paper with citations",
        "category": "extraction_artifacts",
        "chunk_heading": "Impact of Sleep Duration on Cognitive Performance",
        "chunk_text": """Impact of Sleep Duration on Cognitive Performance in Adults

Sarah Chen¹, Michael Roberts², Emma Thompson¹
¹Department of Psychology, University of California
²Sleep Research Center, Stanford Medical School

Received: January 15, 2024
Accepted: March 10, 2024
DOI: 10.1234/sleep.2024.0892

[Download PDF] [Export Citation] [Related Articles]

## Abstract

This study examined the relationship between sleep duration and cognitive performance in 500 adults aged 25-65. Participants underwent comprehensive neuropsychological testing after controlled sleep periods.

## Methods and Results

Participants were divided into three groups based on sleep duration: short sleepers (4-6 hours), normal sleepers (7-8 hours), and long sleepers (9+ hours). Cognitive assessments included:

**Working Memory**: Measured using digit span and n-back tasks. Normal sleepers scored 15% higher than short sleepers (p<0.001).

**Processing Speed**: Trail Making Test showed 23% faster completion times in normal sleepers compared to both short and long sleepers.

**Executive Function**: Wisconsin Card Sorting Test revealed optimal performance at 7.5 hours of sleep, with significant decrements below 6 hours or above 9 hours.

**Attention**: Sustained attention tasks showed linear decline with sleep deprivation. Each hour below 7 hours correlated with 8% decrease in accuracy.

## Clinical Implications

These findings suggest an optimal sleep window of 7-8 hours for peak cognitive performance. Both insufficient and excessive sleep associate with cognitive deficits, supporting a U-shaped relationship.

Healthcare providers should screen for sleep duration when evaluating cognitive complaints. Sleep optimization may serve as a modifiable factor for cognitive health maintenance.

Cite as: Chen S, Roberts M, Thompson E. (2024). Impact of Sleep Duration on Cognitive Performance. J Sleep Cognition. 45(3):234-248.""",
        "expected": {
            "query_answer": {"min": 75, "max": 95, "notes": "Strong research content"},
            "llm_rubric": {"min": 70, "max": 90, "notes": "Ignore academic metadata"},
            "structure_quality": {"min": 75, "max": 95, "notes": "Academic structure"},
            "entity_focus": {"min": 70, "max": 90, "notes": "Medical/research entities"},
            "overall": {"min": 70, "max": 90}
        },
        "notes": "Academic content with author affiliations, DOI, citations, and download buttons"
    },
    
    {
        "id": "diverse_artifact_003",
        "name": "Recipe blog with personal story",
        "category": "extraction_artifacts",
        "chunk_heading": "Grandma's Secret Chocolate Chip Cookies",
        "chunk_text": """Jump to Recipe | Print Recipe | ★★★★★ 4.9 from 2,847 reviews

Every time I make these cookies, I'm transported back to my grandmother's kitchen in Vermont. The smell of butter and vanilla, the warmth of the oven - it all comes flooding back. Last week, my daughter asked if we could make cookies together, and I knew exactly which recipe to share...

[Three paragraphs of childhood memories removed for brevity]

Grandma's Secret Chocolate Chip Cookies

Prep Time: 15 minutes | Cook Time: 12 minutes | Total: 27 minutes
Servings: 48 cookies | Calories: 142 per cookie

## The Secret Ingredient

Grandma's secret was brown butter and a touch of espresso powder. The brown butter adds a nutty depth, while espresso enhances the chocolate without adding coffee flavor.

## Ingredients

- 1 cup (226g) unsalted butter
- 1 cup (200g) light brown sugar, packed
- 1/2 cup (100g) granulated sugar
- 2 large eggs, room temperature
- 2 teaspoons vanilla extract
- 2 1/4 cups (281g) all-purpose flour
- 1 teaspoon baking soda
- 1 teaspoon salt
- 1/2 teaspoon espresso powder
- 2 cups (340g) chocolate chips

## Instructions

1. **Brown the butter**: Melt butter in saucepan over medium heat, stirring constantly until it turns golden brown and smells nutty (5-7 minutes). Cool to room temperature.

2. **Mix wet ingredients**: Combine brown butter with both sugars. Beat in eggs one at a time, then vanilla.

3. **Combine dry ingredients**: Whisk flour, baking soda, salt, and espresso powder.

4. **Form dough**: Fold dry ingredients into wet until just combined. Stir in chocolate chips.

5. **Chill**: Refrigerate dough 30 minutes minimum (up to 72 hours for best flavor).

6. **Bake**: Drop rounded tablespoons onto parchment-lined sheets. Bake at 350°F for 11-12 minutes until edges are golden.

📌 Pin this recipe! | Share on Instagram @foodblogger | Subscribe for weekly recipes!""",
        "expected": {
            "query_answer": {"min": 70, "max": 90, "notes": "Complete recipe despite blog elements"},
            "llm_rubric": {"min": 65, "max": 85, "notes": "Ignore personal story elements"},
            "structure_quality": {"min": 70, "max": 90, "notes": "Good recipe structure"},
            "entity_focus": {"min": 65, "max": 85, "notes": "Ingredients and techniques"},
            "overall": {"min": 70, "max": 90}
        },
        "notes": "Recipe with personal blog story, ratings, social buttons, and nutritional info"
    },
    
    {
        "id": "diverse_artifact_004",
        "name": "Product review with badges",
        "category": "extraction_artifacts",
        "chunk_heading": "Review: EcoFlow Portable Solar Generator",
        "chunk_text": """⭐⭐⭐⭐⭐ 4.5 out of 5 stars | 1,234 reviews
✓ Verified Purchase | ✓ Early Reviewer Rewards

Reviewed by: TechDad42
Review Date: February 15, 2024
Helpful? 👍 156 👎 12

[Badge: Top 1000 Reviewer] [Badge: Helpful Reviews: 50+]

## Perfect for Off-Grid Adventures

After using the EcoFlow Delta 2 for six months, I can confidently say it's transformed our camping experience. This 1024Wh portable power station paired with their 220W solar panel has been incredibly reliable.

## Real-World Performance

The unit charges from 0-80% in just 50 minutes via AC outlet, exactly as advertised. Solar charging varies by conditions but typically achieves full charge in 4-6 hours of direct sunlight. During our week-long camping trip, it powered:

- CPAP machine: 8 hours nightly (60W)
- 12V refrigerator: Continuous (45W average)
- LED lights: 6 hours daily (20W total)
- Phone/tablet charging: Multiple devices (30W)
- Coffee maker: 15 minutes daily (600W)

Battery retained 15% capacity after this usage pattern with daily solar recharging.

## Build Quality and Features

The construction feels premium with a sturdy handle and rubberized corners. The LCD display clearly shows input/output wattage, remaining capacity, and time estimates. The EcoFlow app provides remote monitoring and control via Bluetooth.

Multiple output options include:
- 4 AC outlets (1800W continuous, 2700W surge)
- 2 USB-C PD ports (100W max)
- 4 USB-A ports
- 12V car outlet

## Minor Drawbacks

The fan noise is noticeable when charging or under heavy load. At 27 pounds, it's portable but not lightweight. Price point is premium compared to competitors.

Was this review helpful? Share your thoughts in the comments!
🛒 See current price | 📊 Compare models | 📧 Email to friend""",
        "expected": {
            "query_answer": {"min": 70, "max": 90, "notes": "Detailed product review"},
            "llm_rubric": {"min": 70, "max": 90, "notes": "Ignore review badges"},
            "structure_quality": {"min": 70, "max": 90, "notes": "Well-organized review"},
            "entity_focus": {"min": 70, "max": 90, "notes": "Product specifications"},
            "overall": {"min": 70, "max": 90}
        },
        "notes": "Product review with star ratings, badges, verified purchase, and engagement buttons"
    },
    
    {
        "id": "diverse_artifact_005",
        "name": "Medical article with disclaimers",
        "category": "extraction_artifacts",
        "chunk_heading": "Understanding Type 2 Diabetes Management",
        "chunk_text": """⚕️ Medically reviewed by Dr. Amanda Richardson, MD, Endocrinologist
Last updated: March 20, 2024
Reading time: 8 minutes

⚠️ This article is for informational purposes only and does not constitute medical advice. Always consult your healthcare provider for personalized treatment.

Understanding Type 2 Diabetes Management

Type 2 diabetes affects how your body processes blood sugar (glucose). With proper management, people with diabetes can live healthy, active lives. Here's what you need to know about modern treatment approaches.

## Blood Sugar Monitoring

Target blood glucose ranges vary by individual, but general guidelines include:
- Fasting: 80-130 mg/dL
- 2 hours after meals: Under 180 mg/dL
- A1C goal: Below 7% for most adults

Continuous glucose monitors (CGMs) like the Dexcom G7 or FreeStyle Libre 3 provide real-time readings every 5 minutes, alerting users to trends before problematic highs or lows occur.

## Medication Options

**Metformin** remains the first-line medication, improving insulin sensitivity and reducing glucose production. Common side effects include gastrointestinal upset, usually temporary.

**GLP-1 agonists** (Ozempic, Trulicity) offer dual benefits: blood sugar control and weight loss. Injectable weekly, they slow digestion and increase insulin production when needed.

**SGLT2 inhibitors** (Jardiance, Farxiga) help kidneys remove excess glucose through urine. Additional benefits include cardiovascular and kidney protection.

## Lifestyle Modifications

Diet: Focus on consistent carbohydrate intake (45-60g per meal), emphasizing whole grains, vegetables, and lean proteins. The plate method suggests 1/2 vegetables, 1/4 protein, 1/4 carbohydrates.

Exercise: Aim for 150 minutes weekly of moderate activity. Resistance training twice weekly improves insulin sensitivity by 25%.

[!] Important: Never adjust medications without medical supervision. Monitor for hypoglycemia symptoms.

💬 Join our diabetes support community | 📱 Download our tracking app | 📧 Subscribe to updates""",
        "expected": {
            "query_answer": {"min": 75, "max": 95, "notes": "Comprehensive medical guide"},
            "llm_rubric": {"min": 70, "max": 90, "notes": "Ignore medical disclaimers"},
            "structure_quality": {"min": 75, "max": 95, "notes": "Clear medical information"},
            "entity_focus": {"min": 75, "max": 95, "notes": "Specific medications and values"},
            "overall": {"min": 75, "max": 95}
        },
        "notes": "Medical content with review attribution, disclaimers, warnings, and CTAs"
    },
    
    {
        "id": "diverse_artifact_006",
        "name": "Travel blog with affiliate links",
        "category": "extraction_artifacts",
        "chunk_heading": "48 Hours in Barcelona: The Perfect Itinerary",
        "chunk_text": """📍 Barcelona, Spain | 🗓️ Best Time: April-June
Written by Travel With Sarah | Photography by @wanderlens
*This post contains affiliate links. I may earn a commission at no extra cost to you.*

[Instagram embed: Beautiful Sagrada Familia sunset photo]
♥️ 15,234 likes

48 Hours in Barcelona: The Perfect Itinerary

Barcelona combines stunning architecture, incredible food, and Mediterranean charm. Here's how to maximize your 48-hour visit.

## Day 1: Gaudí and Gothic Quarter

**Morning (9 AM)**: Start at Sagrada Familia (book tickets in advance*). Gaudí's masterpiece requires 2-3 hours. The tower climb offers spectacular city views. Audio guide explains the intricate symbolism.
*Book through GetYourGuide (affiliate link) for skip-the-line access

**Lunch (12:30 PM)**: Walk to Cervecería Catalana for tapas. Order patatas bravas (€6), pan con tomate (€4), and croquetas de jamón (€8). Expect 30-minute wait on weekends.

**Afternoon (2 PM)**: Explore the Gothic Quarter's narrow medieval streets. Key stops:
- Barcelona Cathedral (free entry 5-7:30 PM, otherwise €9)
- Plaça Sant Jaume (government buildings)
- Pont del Bisbe (Instagram-famous bridge)

**Evening (7 PM)**: Sunset at Park Güell upper area (free access). The paid monumental zone (€10) closes at sunset but surrounding areas offer equally stunning views.

## Day 2: Beaches and Modernisme

**Morning (10 AM)**: La Boqueria Market for breakfast. Try xuixo pastry (€2) and fresh juice (€4). Purchase jamón ibérico for later picnic.

**Midday (11:30 AM)**: Walk down Las Ramblas to Barceloneta Beach. Rent bikes (€10/day) to explore the 4.5km waterfront to Poblenou.

[Ad: Barcelona City Pass - Save 20% on attractions!]

**Afternoon (3 PM)**: Casa Batlló or Casa Milà on Passeig de Gràcia. Both offer augmented reality experiences. Casa Batlló's "10D Experience" is particularly immersive (€35).

Pro tip: Download my free Barcelona guide! 📱
Follow @TravelWithSarah for daily travel tips""",
        "expected": {
            "query_answer": {"min": 70, "max": 90, "notes": "Detailed travel itinerary"},
            "llm_rubric": {"min": 70, "max": 90, "notes": "Ignore affiliate disclaimers"},
            "structure_quality": {"min": 70, "max": 90, "notes": "Well-planned itinerary"},
            "entity_focus": {"min": 75, "max": 95, "notes": "Specific places and prices"},
            "overall": {"min": 70, "max": 90}
        },
        "notes": "Travel content with Instagram embeds, affiliate links, ads, and social media plugs"
    },
    
    {
        "id": "diverse_artifact_007",
        "name": "Business report with copyright",
        "category": "extraction_artifacts",
        "chunk_heading": "Q3 2024 Retail Industry Analysis",
        "chunk_text": """[Company Logo: Strategic Insights Group]

Q3 2024 Retail Industry Analysis

Prepared by: Strategic Insights Group
Date: October 15, 2024
Distribution: Confidential - Client Use Only

© 2024 Strategic Insights Group. All rights reserved. No part of this publication may be reproduced without written permission.

## Executive Summary

The retail sector demonstrated resilience in Q3 2024, with overall sales growth of 4.2% year-over-year despite ongoing economic headwinds. E-commerce continues capturing market share, now representing 23% of total retail sales.

## Key Performance Metrics

**Total Retail Sales**: $1.82 trillion (Q3)
- Online: $418.6 billion (+12% YoY)
- Brick-and-mortar: $1.40 trillion (+2% YoY)

**Category Performance**:
- Electronics: +8.5% (driven by AI-enabled devices)
- Apparel: +3.2% (recovery from 2023 lows)
- Home goods: -1.5% (housing market impact)
- Groceries: +5.1% (inflation-adjusted: +1.8%)

## Consumer Behavior Shifts

Mobile commerce now accounts for 44% of online sales, up from 38% in Q3 2023. Buy-online-pickup-in-store (BOPIS) adoption reached 67% among major retailers, with same-day fulfillment becoming the competitive standard.

Generation Z consumers (ages 12-27) drove social commerce growth, with TikTok Shop and Instagram Shopping generating $12 billion in quarterly sales. Sustainability remains a key purchase driver for 73% of millennials.

## Market Leaders

Amazon maintained 37.8% e-commerce market share. Walmart's omnichannel strategy yielded 6.4% comparable sales growth. Target's same-day services accounted for 25% of digital sales. Specialty retailers like Ulta Beauty and Lululemon outperformed with 12% and 15% growth respectively.

[Footer: Page 1 of 12 | Property of Strategic Insights Group | www.strategicinsights.com]""",
        "expected": {
            "query_answer": {"min": 70, "max": 90, "notes": "Strong business analysis"},
            "llm_rubric": {"min": 70, "max": 90, "notes": "Ignore corporate formatting"},
            "structure_quality": {"min": 75, "max": 95, "notes": "Professional report structure"},
            "entity_focus": {"min": 70, "max": 90, "notes": "Companies and metrics"},
            "overall": {"min": 70, "max": 90}
        },
        "notes": "Business report with logo descriptions, copyright notices, and corporate formatting"
    },
    
    {
        "id": "diverse_artifact_008",
        "name": "Educational content with quiz widget",
        "category": "extraction_artifacts",
        "chunk_heading": "The American Civil War: Causes and Consequences",
        "chunk_text": """📚 History 101 | Grade Level: 9-12 | Duration: 45 minutes
👤 Created by: Mr. Johnson | Last Modified: September 2024
🖨️ Print Lesson | 📧 Email to Students | 📊 View Standards Alignment

[Interactive Timeline Widget: 1861-1865]

The American Civil War: Causes and Consequences

The American Civil War (1861-1865) remains the deadliest conflict in U.S. history, fundamentally transforming the nation's political, social, and economic landscape.

## Primary Causes

**Slavery and States' Rights**: The fundamental dispute centered on whether states could maintain slavery as they expanded westward. The Missouri Compromise (1820) and Kansas-Nebraska Act (1854) attempted unsuccessful solutions.

**Economic Differences**: The industrial North's wage-labor economy clashed with the South's agricultural system dependent on enslaved labor. By 1860, the South produced 75% of world cotton exports using 4 million enslaved people.

**Political Crisis**: Lincoln's 1860 election without winning a single Southern state triggered secession. South Carolina seceded December 20, 1860, followed by ten more states forming the Confederate States of America.

## Major Turning Points

**Fort Sumter (April 12, 1861)**: Confederate attack began the war
**Antietam (September 17, 1862)**: Bloodiest single day, enabled Emancipation Proclamation
**Gettysburg (July 1-3, 1863)**: Ended Confederate invasion of North
**Sherman's March (November-December 1864)**: Total war strategy devastated South

[Quiz Widget: Test Your Knowledge! 10 Questions]

## Lasting Consequences

The war's 620,000-750,000 deaths exceeded all other American wars combined. The 13th, 14th, and 15th Amendments abolished slavery, granted citizenship, and protected voting rights. Reconstruction (1865-1877) attempted to rebuild the South and integrate freed slaves.

Economic impacts included the South's devastation, losing 60% of its wealth, while Northern industry boomed. The federal government's power expanded permanently, settling the states' rights debate.

📝 Download worksheet | 🎥 Watch documentary | 🎮 Play Civil War simulation game
Next Lesson: Reconstruction Era →""",
        "expected": {
            "query_answer": {"min": 75, "max": 95, "notes": "Comprehensive history lesson"},
            "llm_rubric": {"min": 70, "max": 90, "notes": "Ignore educational widgets"},
            "structure_quality": {"min": 75, "max": 95, "notes": "Clear educational structure"},
            "entity_focus": {"min": 75, "max": 95, "notes": "Historical events and dates"},
            "overall": {"min": 75, "max": 95}
        },
        "notes": "Educational content with quiz widgets, print buttons, standards alignment, and interactive elements"
    }
]