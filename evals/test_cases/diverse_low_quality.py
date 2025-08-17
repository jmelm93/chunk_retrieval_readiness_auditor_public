"""Low quality test cases from diverse non-technical domains."""

DIVERSE_LOW_QUALITY_CASES = [
    {
        "id": "diverse_low_001",
        "name": "Medical disclaimer only",
        "category": "low_quality",
        "chunk_heading": "Health Information Disclaimer",
        "chunk_text": """This information is for educational purposes only. Not intended as medical advice. Consult your healthcare provider. 

Individual results may vary. Not evaluated by the FDA. Does not diagnose, treat, cure, or prevent any disease.

Always seek professional medical advice. Never disregard medical advice. Do not delay seeking treatment.

We are not responsible for any adverse effects. Use at your own risk. Discontinue use if problems occur.

Copyright notice: All rights reserved. No reproduction without permission. Subject to terms and conditions.""",
        "expected": {
            "query_answer": {"min": 0, "max": 20, "notes": "Pure disclaimer, no content"},
            "llm_rubric": {"min": 0, "max": 20, "notes": "No informational value"},
            "structure_quality": {"min": 25, "max": 45, "notes": "Basic structure only"},
            "entity_focus": {"min": 0, "max": 20, "notes": "No medical entities"},
            "overall": {"min": 5, "max": 25}
        },
        "notes": "Generic medical disclaimer with no actual health information"
    },
    
    {
        "id": "diverse_low_002",
        "name": "Legal boilerplate terms",
        "category": "low_quality",
        "chunk_heading": "",
        "chunk_text": """By using this service you agree to these terms. We reserve the right to modify terms at any time. Continued use constitutes acceptance.

We provide service "as is" without warranties. Not liable for damages. You indemnify us from all claims.

Governing law applies. Disputes resolved through arbitration. Class actions waived. 

Severability clause applies. Entire agreement supersedes prior agreements. Notices must be in writing.

© All rights reserved. Trademarks property of respective owners. Unauthorized use prohibited.""",
        "expected": {
            "query_answer": {"min": 0, "max": 20, "notes": "Boilerplate legal text"},
            "llm_rubric": {"min": 5, "max": 25, "notes": "No specific information"},
            "structure_quality": {"min": 20, "max": 40, "notes": "No heading, generic format"},
            "entity_focus": {"min": 0, "max": 20, "notes": "No specific entities"},
            "overall": {"min": 5, "max": 25}
        },
        "notes": "Standard legal boilerplate without specific terms or context"
    },
    
    {
        "id": "diverse_low_003",
        "name": "Restaurant menu items only",
        "category": "low_quality",
        "chunk_heading": "Menu",
        "chunk_text": """Appetizers
Spring Rolls - $8
Soup of the Day - $6
Caesar Salad - $9
Bruschetta - $7

Main Courses  
Grilled Salmon - $24
Chicken Parmesan - $18
Vegetable Pasta - $16
Ribeye Steak - $32

Desserts
Chocolate Cake - $8
Ice Cream - $6
Tiramisu - $9

Beverages
Coffee - $3
Tea - $3
Soft Drinks - $4
Wine - From $8""",
        "expected": {
            "query_answer": {"min": 10, "max": 30, "notes": "Just menu items and prices"},
            "llm_rubric": {"min": 10, "max": 30, "notes": "No descriptions"},
            "structure_quality": {"min": 40, "max": 60, "notes": "Basic menu structure"},
            "entity_focus": {"min": 30, "max": 50, "notes": "Food items but no context"},
            "overall": {"min": 15, "max": 35}
        },
        "notes": "Basic menu listing without descriptions or restaurant information"
    },
    
    {
        "id": "diverse_low_004",
        "name": "Weather forecast stub",
        "category": "low_quality",
        "chunk_heading": "Weather",
        "chunk_text": """Today: Partly cloudy. High 72°F. Low 58°F.

Tomorrow: Sunny. High 75°F. Low 60°F.

Thursday: Chance of rain. High 68°F. Low 55°F.

Friday: Cloudy. High 70°F. Low 57°F.""",
        "expected": {
            "query_answer": {"min": 15, "max": 35, "notes": "Minimal weather data"},
            "llm_rubric": {"min": 15, "max": 35, "notes": "Very basic information"},
            "structure_quality": {"min": 35, "max": 55, "notes": "Simple format"},
            "entity_focus": {"min": 10, "max": 30, "notes": "No location specified"},
            "overall": {"min": 15, "max": 35}
        },
        "notes": "Basic weather forecast without location or detailed conditions"
    },
    
    {
        "id": "diverse_low_005",
        "name": "E-commerce category listing",
        "category": "low_quality",
        "chunk_heading": "Shop by Category",
        "chunk_text": """Electronics
- Computers & Tablets
- Phones & Accessories
- TVs & Home Theater
- Cameras & Photography

Home & Garden
- Furniture
- Kitchen & Dining
- Bedding & Bath
- Outdoor & Patio

Fashion
- Women's Clothing
- Men's Clothing
- Shoes
- Accessories

Sports & Outdoors
- Exercise & Fitness
- Camping & Hiking
- Team Sports
- Water Sports

View All Categories >""",
        "expected": {
            "query_answer": {"min": 5, "max": 25, "notes": "Just category navigation"},
            "llm_rubric": {"min": 5, "max": 25, "notes": "No product information"},
            "structure_quality": {"min": 35, "max": 55, "notes": "Category structure only"},
            "entity_focus": {"min": 15, "max": 35, "notes": "Generic categories"},
            "overall": {"min": 10, "max": 30}
        },
        "notes": "E-commerce category navigation without products or descriptions"
    },
    
    {
        "id": "diverse_low_006",
        "name": "Event calendar dates only",
        "category": "low_quality",
        "chunk_heading": "",
        "chunk_text": """Upcoming Events:

March 15 - Board Meeting
March 18 - Community Workshop
March 22 - Annual Fundraiser
March 25 - Training Session

April 2 - Spring Festival
April 8 - Member Meeting
April 14 - Special Event
April 20 - Conference

May 5 - Celebration
May 12 - Workshop
May 18 - Networking Event
May 28 - Holiday Closure

For more information visit our website.""",
        "expected": {
            "query_answer": {"min": 5, "max": 25, "notes": "Dates without details"},
            "llm_rubric": {"min": 10, "max": 30, "notes": "No event descriptions"},
            "structure_quality": {"min": 20, "max": 40, "notes": "Missing heading"},
            "entity_focus": {"min": 5, "max": 25, "notes": "Generic event names"},
            "overall": {"min": 10, "max": 30}
        },
        "notes": "Event calendar without descriptions, times, or locations"
    },
    
    {
        "id": "diverse_low_007",
        "name": "Business directory names only",
        "category": "low_quality",
        "chunk_heading": "Local Business Directory",
        "chunk_text": """A
Ace Hardware
Amy's Flowers
Anderson Law Firm

B
Bob's Auto Repair
Bella's Restaurant
Brown Dental Clinic

C
City Bank
Coffee Corner
Clark's Pharmacy

D
Downtown Books
Dave's Pizza
Davis Insurance

E
Elite Fitness
Emma's Boutique
Express Cleaners

See full directory online.""",
        "expected": {
            "query_answer": {"min": 0, "max": 20, "notes": "Just business names"},
            "llm_rubric": {"min": 5, "max": 25, "notes": "No business information"},
            "structure_quality": {"min": 30, "max": 50, "notes": "Alphabetical structure"},
            "entity_focus": {"min": 20, "max": 40, "notes": "Business names without context"},
            "overall": {"min": 10, "max": 30}
        },
        "notes": "Business directory listing without addresses, phone numbers, or descriptions"
    }
]