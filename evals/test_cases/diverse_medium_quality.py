"""Medium quality test cases from diverse non-technical domains."""

DIVERSE_MEDIUM_QUALITY_CASES = [
    {
        "id": "diverse_medium_001",
        "name": "News article with poor attribution",
        "category": "medium_quality",
        "chunk_heading": "Economic Recovery Shows Mixed Signals",
        "chunk_text": """The economy is showing signs of recovery according to recent reports. Experts say that various indicators point to improvement, though some challenges remain.

Employment figures have been better than expected. Many sectors are hiring again, and unemployment is down from where it was. However, as noted in earlier analyses, certain industries continue to struggle.

Consumer spending has increased in recent months. People are buying more goods and services, which helps businesses. Retail sales data confirms this trend, though the numbers vary by region.

Inflation remains a concern for policymakers. Prices have risen for many items, affecting household budgets. The central bank is monitoring the situation closely and may adjust its approach as discussed previously.

Housing markets show varied performance across the country. Some areas see strong demand and rising prices, while others lag behind. This pattern reflects broader economic disparities mentioned in our previous coverage.

Analysts remain cautiously optimistic about the outlook. Most believe growth will continue, though at a moderate pace. The factors outlined above will play key roles in determining the trajectory.""",
        "expected": {
            "query_answer": {"min": 45, "max": 65, "notes": "Vague without specific data"},
            "llm_rubric": {"min": 50, "max": 70, "notes": "Generic economic commentary"},
            "structure_quality": {"min": 60, "max": 80, "notes": "Organized but lacks depth"},
            "entity_focus": {"min": 30, "max": 50, "notes": "No specific companies or figures"},
            "overall": {"min": 45, "max": 65}
        },
        "notes": "Generic news article lacking specific data, sources, or concrete examples"
    },
    
    {
        "id": "diverse_medium_002",
        "name": "E-commerce product lacking specifications",
        "category": "medium_quality",
        "chunk_heading": "Premium Leather Handbag Collection",
        "chunk_text": """Our premium leather handbag is a perfect accessory for any occasion. Made from high-quality materials, this bag combines style and functionality.

The bag features multiple compartments for organization. You can store all your essentials easily. The main compartment is spacious, and there are several pockets for smaller items.

Available in various colors to match your style. The classic design works well with both casual and formal outfits. The leather develops a beautiful patina over time.

Features:
- Genuine leather construction
- Multiple compartments
- Adjustable strap
- Quality hardware
- Interior lining

This handbag is ideal for daily use or special occasions. It makes a great gift for someone special. The craftsmanship ensures long-lasting durability.

Care is simple - just wipe with a damp cloth occasionally. Store in the provided dust bag when not in use. With proper care, this bag will last for years.

Customer reviews praise the quality and style. Many say it's their favorite bag. The versatility makes it a worthwhile investment.""",
        "expected": {
            "query_answer": {"min": 50, "max": 70, "notes": "Missing key specifications"},
            "llm_rubric": {"min": 50, "max": 70, "notes": "Generic product description"},
            "structure_quality": {"min": 65, "max": 85, "notes": "Decent structure"},
            "entity_focus": {"min": 35, "max": 55, "notes": "No brand or specific details"},
            "overall": {"min": 50, "max": 70}
        },
        "notes": "Product description missing dimensions, weight, price, brand, and specific features"
    },
    
    {
        "id": "diverse_medium_003",
        "name": "Travel guide with vague recommendations",
        "category": "medium_quality",
        "chunk_heading": "Exploring Mediterranean Coastal Towns",
        "chunk_text": """The Mediterranean coast offers beautiful destinations for travelers seeking sun, sea, and culture. These charming towns provide unique experiences throughout the region.

The beaches here are stunning with crystal-clear waters. You can spend days relaxing on the sand or swimming. Water sports are popular activities in many locations. The coastal scenery is breathtaking.

Local cuisine is a highlight of visiting these areas. Fresh seafood is available everywhere. Traditional dishes vary by region but are always delicious. Don't miss trying the local specialties mentioned in other guides.

Historical sites are abundant along the coast. Ancient ruins and medieval architecture tell stories of the past. Museums showcase regional art and culture. Walking tours help you explore the heritage.

The best time to visit depends on your preferences. Summer is busiest but offers warm weather and festivals. Spring and fall have fewer crowds and mild temperatures. Winter can be quiet but some attractions may be closed.

Accommodation ranges from budget to luxury options. Coastal hotels offer sea views. Vacation rentals provide more space for families. Book early during peak season as described in our planning section.

Getting around is relatively easy. Public transportation connects major towns. Renting a car gives more flexibility for exploring. Boats provide scenic routes between coastal destinations.""",
        "expected": {
            "query_answer": {"min": 40, "max": 60, "notes": "Too vague, no specific locations"},
            "llm_rubric": {"min": 45, "max": 65, "notes": "Generic travel content"},
            "structure_quality": {"min": 60, "max": 80, "notes": "Organized topics"},
            "entity_focus": {"min": 25, "max": 45, "notes": "No specific places named"},
            "overall": {"min": 45, "max": 65}
        },
        "notes": "Travel guide without specific towns, attractions, restaurants, or practical details"
    },
    
    {
        "id": "diverse_medium_004",
        "name": "Sports recap missing key statistics",
        "category": "medium_quality",
        "chunk_heading": "Championship Game Delivers Thrilling Finish",
        "chunk_text": """Last night's championship game provided fans with an exciting conclusion to the season. Both teams played with intensity, creating memorable moments throughout the contest. The atmosphere in the stadium was electric as the game went down to the wire. Players from both sides gave their maximum effort in pursuit of the title. The coaching strategies employed by both teams reflected the high stakes of the matchup. Key players stepped up when it mattered most, making crucial plays in important moments. The defense was particularly impressive, with several game-changing stops. Offensive execution improved as the game progressed, leading to scoring opportunities. Special teams also contributed to the outcome with solid performances. The crowd's energy influenced the game's momentum at various points. Injuries played a role, as noted in the injury report, affecting both teams' rotations. The referee's decisions were controversial at times, sparking debate among fans and analysts. Weather conditions were favorable, allowing both teams to execute their game plans. This victory adds to the winning team's legacy, as discussed in historical context. The losing team showed resilience despite falling short of their ultimate goal.""",
        "expected": {
            "query_answer": {"min": 35, "max": 55, "notes": "No scores or specific plays"},
            "llm_rubric": {"min": 40, "max": 60, "notes": "Vague sports commentary"},
            "structure_quality": {"min": 40, "max": 60, "notes": "Wall of text format"},
            "entity_focus": {"min": 20, "max": 40, "notes": "No team names or players"},
            "overall": {"min": 35, "max": 55}
        },
        "notes": "Sports recap without scores, team names, player names, or specific statistics"
    },
    
    {
        "id": "diverse_medium_005",
        "name": "Environmental article with unclear data",
        "category": "medium_quality",
        "chunk_heading": "Climate Impact on Regional Ecosystems",
        "chunk_text": """Climate change is affecting ecosystems in various ways across the region. Scientists have observed changes in wildlife patterns and plant growth cycles over recent years.

Temperature increases have been recorded throughout the area. These changes impact both terrestrial and aquatic environments. Species are adapting to new conditions in different ways. Some are thriving while others face challenges.

Precipitation patterns have shifted significantly. Some areas receive more rainfall while others experience drought. This affects water availability for wildlife and vegetation. The changes discussed in previous studies continue to evolve.

Wildlife migration patterns show notable alterations:
- Birds arriving earlier or later than usual
- Mammals changing their range
- Fish populations moving to different areas
- Insects emerging at different times

Plant communities are responding to climate shifts. Growing seasons have changed in many locations. Some species are expanding their range while others decline. Forest composition is gradually changing.

Conservation efforts are underway to address these challenges. Various organizations work to protect vulnerable species. Habitat restoration projects help maintain ecosystem balance. Community involvement increases awareness and support.

More research is needed to fully understand long-term impacts. Monitoring programs track ongoing changes. Data collection helps inform management decisions.""",
        "expected": {
            "query_answer": {"min": 50, "max": 70, "notes": "Vague environmental claims"},
            "llm_rubric": {"min": 50, "max": 70, "notes": "Lacks specific data"},
            "structure_quality": {"min": 65, "max": 85, "notes": "Clear sections"},
            "entity_focus": {"min": 30, "max": 50, "notes": "No specific locations or species"},
            "overall": {"min": 50, "max": 70}
        },
        "notes": "Environmental article without specific data, locations, or quantified impacts"
    },
    
    {
        "id": "diverse_medium_006",
        "name": "Real estate listing with incomplete details",
        "category": "medium_quality",
        "chunk_heading": "Charming Family Home in Desirable Neighborhood",
        "chunk_text": """This beautiful home offers everything a family needs in a great location. The property features spacious rooms and modern amenities throughout.

The living spaces are bright and welcoming. Large windows provide natural light. The floor plan flows well for entertaining. Storage space is ample throughout the home.

The kitchen has been updated with quality appliances. Counter space is generous for meal preparation. The dining area accommodates family gatherings. Cabinet storage meets household needs.

Bedrooms are comfortable and well-sized. The master suite includes an ensuite bathroom. Closet space is adequate in all rooms. Natural light brightens each bedroom.

Outdoor space includes a yard perfect for children and pets. The patio area works well for barbecues. Landscaping is established and attractive. Privacy from neighbors is reasonable.

The neighborhood offers excellent amenities:
- Good schools nearby
- Shopping within easy reach
- Parks and recreation close by
- Public transportation available

This property has been well-maintained by current owners. Updates have been made over the years. The home is move-in ready. Schedule a viewing to appreciate all features.""",
        "expected": {
            "query_answer": {"min": 45, "max": 65, "notes": "Missing key details"},
            "llm_rubric": {"min": 45, "max": 65, "notes": "Vague property description"},
            "structure_quality": {"min": 60, "max": 80, "notes": "Organized sections"},
            "entity_focus": {"min": 25, "max": 45, "notes": "No specific location or specs"},
            "overall": {"min": 45, "max": 65}
        },
        "notes": "Real estate listing without square footage, bedrooms, bathrooms, price, or address"
    },
    
    {
        "id": "diverse_medium_007",
        "name": "Movie review without concrete examples",
        "category": "medium_quality",
        "chunk_heading": "Film Review: Latest Drama Captures Hearts",
        "chunk_text": """The latest drama to hit theaters delivers an emotional journey that resonates with audiences. The film explores themes of family, redemption, and personal growth through its compelling narrative.

The performances are noteworthy across the board. The lead actor brings depth to their character. Supporting cast members contribute meaningfully to the story. The chemistry between actors feels authentic and engaging.

Direction shows skillful handling of dramatic moments. Pacing keeps viewers engaged throughout. Visual storytelling complements the dialogue effectively. The filmmaker's vision comes through clearly.

The screenplay balances drama with lighter moments. Dialogue feels natural and purposeful. Character development unfolds organically. Plot points connect well as mentioned in other reviews.

Technical aspects enhance the viewing experience:
- Cinematography captures beautiful scenes
- Music score supports emotional beats
- Editing maintains good rhythm
- Sound design adds atmosphere

Themes resonate with contemporary audiences. The story addresses relevant social issues. Character struggles feel relatable. The resolution provides satisfaction while leaving room for thought.

This film stands out in the current dramatic landscape. It offers something for various audience segments. The overall experience justifies the theatrical viewing. Awards consideration seems likely given the quality.""",
        "expected": {
            "query_answer": {"min": 40, "max": 60, "notes": "No specific scenes or quotes"},
            "llm_rubric": {"min": 45, "max": 65, "notes": "Generic film commentary"},
            "structure_quality": {"min": 65, "max": 85, "notes": "Well-organized review"},
            "entity_focus": {"min": 20, "max": 40, "notes": "No names or film title"},
            "overall": {"min": 45, "max": 65}
        },
        "notes": "Movie review without film title, actor names, director, or specific scenes"
    },
    
    {
        "id": "diverse_medium_008",
        "name": "Fitness routine lacking form descriptions",
        "category": "medium_quality",
        "chunk_heading": "Full Body Workout Program",
        "chunk_text": """This workout program targets all major muscle groups for comprehensive fitness development. Perform this routine three times per week with rest days between sessions.

Warm-up is essential before starting exercises. Spend time preparing your body for the workout. Include dynamic movements and stretching. This prevents injury and improves performance.

Upper Body Exercises:
- Push-up variations for chest and arms
- Pull exercises for back development
- Shoulder movements for deltoid strength
- Arm exercises for biceps and triceps

Lower Body Exercises:
- Squatting movements for legs
- Lunging patterns for balance
- Calf raises for lower leg strength
- Hip exercises for glute development

Core Training:
- Plank variations for stability
- Rotational movements for obliques
- Lower ab exercises
- Back strengthening movements

Perform each exercise for the recommended sets and reps. Rest between sets as needed. Adjust intensity based on fitness level. Progress gradually as discussed in training principles.

Cool-down after completing the workout. Include stretching for all muscle groups. Hydrate properly throughout. Recovery is important for results.""",
        "expected": {
            "query_answer": {"min": 45, "max": 65, "notes": "Missing form instructions"},
            "llm_rubric": {"min": 50, "max": 70, "notes": "Vague exercise descriptions"},
            "structure_quality": {"min": 65, "max": 85, "notes": "Good workout structure"},
            "entity_focus": {"min": 40, "max": 60, "notes": "Generic exercise names"},
            "overall": {"min": 50, "max": 70}
        },
        "notes": "Workout routine without specific form cues, rep ranges, or rest periods"
    }
]