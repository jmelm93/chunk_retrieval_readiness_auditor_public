"""Low quality test cases expected to score poorly."""

LOW_QUALITY_CASES = [
    {
        "id": "low_001",
        "name": "Navigation menu only",
        "category": "low_quality",
        "chunk_heading": "Site Navigation",
        "chunk_text": """Home | About | Services | Blog | Contact

Products
- Software Solutions
- Consulting Services  
- Training Programs
- Support Packages

Company
- About Us
- Leadership Team
- Careers
- Press Releases

Resources
- Documentation
- Downloads
- Community Forum
- Knowledge Base

Legal
- Privacy Policy
- Terms of Service
- Cookie Policy
- Accessibility""",
        "expected": {
            "query_answer": {"min": 0, "max": 20, "notes": "No actual content, just navigation"},
            "llm_rubric": {"min": 0, "max": 20, "notes": "Not suitable for retrieval"},
            "structure_quality": {"min": 30, "max": 50, "notes": "Structure exists but no content"},
            "entity_focus": {"min": 0, "max": 20, "notes": "Only navigation labels"},
            "overall": {"min": 0, "max": 25}
        },
        "notes": "Pure navigation menu with no informational content"
    },
    
    {
        "id": "low_002",
        "name": "Footer with links only",
        "category": "low_quality",
        "chunk_heading": "",
        "chunk_text": """© 2024 TechCorp Inc. All rights reserved.

Follow Us:
Facebook | Twitter | LinkedIn | Instagram | YouTube

Newsletter Signup
Enter your email to receive updates

Contact Info:
Email: info@techcorp.com
Phone: 1-800-TECH-CORP
Address: 123 Tech Street, Silicon Valley, CA 94025

Site Links:
Privacy Policy | Terms of Use | Cookie Settings | Accessibility Statement | Sitemap

Partner Links:
AWS Partner Network | Microsoft Partner | Google Cloud Partner | IBM Partner Network""",
        "expected": {
            "query_answer": {"min": 0, "max": 20, "notes": "Footer content not informative"},
            "llm_rubric": {"min": 0, "max": 20, "notes": "No retrieval value"},
            "structure_quality": {"min": 20, "max": 40, "notes": "Missing heading"},
            "entity_focus": {"min": 10, "max": 30, "notes": "Company names but no context"},
            "overall": {"min": 5, "max": 25}
        },
        "notes": "Typical website footer with no substantial content"
    },
    
    {
        "id": "low_003",
        "name": "Extremely short content",
        "category": "low_quality",
        "chunk_heading": "Introduction",
        "chunk_text": """Welcome to our platform. We provide solutions for businesses.""",
        "expected": {
            "query_answer": {"min": 10, "max": 30, "notes": "Too vague and short"},
            "llm_rubric": {"min": 10, "max": 30, "notes": "Insufficient content"},
            "structure_quality": {"min": 30, "max": 50, "notes": "Minimal structure"},
            "entity_focus": {"min": 0, "max": 20, "notes": "No specific entities"},
            "overall": {"min": 10, "max": 30}
        },
        "notes": "Extremely short and vague, provides no useful information"
    },
    
    {
        "id": "low_004",
        "name": "No clear topic focus",
        "category": "low_quality",
        "chunk_heading": "Miscellaneous Information",
        "chunk_text": """The weather today is partly cloudy with a chance of rain. Our office will be closed next Monday for the holiday. 

Don't forget to update your passwords regularly for security. The new coffee machine is installed in the break room.

Sales figures for Q3 showed improvement. We're hiring for several positions - check the careers page. The parking lot will be repaved next week.

Remember to submit your timesheets by Friday. The company picnic has been rescheduled to next month. IT support is available from 9 AM to 5 PM.

Project deadlines are approaching. Please review the updated policies. Training sessions are mandatory for all staff.""",
        "expected": {
            "query_answer": {"min": 10, "max": 30, "notes": "No coherent topic"},
            "llm_rubric": {"min": 15, "max": 35, "notes": "Multiple unrelated topics"},
            "structure_quality": {"min": 30, "max": 50, "notes": "Random organization"},
            "entity_focus": {"min": 5, "max": 25, "notes": "Scattered, unrelated entities"},
            "overall": {"min": 15, "max": 35}
        },
        "notes": "Random collection of unrelated announcements with no focus"
    },
    
    {
        "id": "low_005",
        "name": "Missing heading with scattered content",
        "category": "low_quality",
        "chunk_heading": "",
        "chunk_text": """Click here to learn more. See our latest updates below. 

Important: This feature is deprecated and will be removed in the next version.

For more information, refer to the documentation. Contact support if you have questions.

Note: Some users may experience issues with this functionality. We're working on a fix.

Try our new features today! Limited time offer available.

Warning: This action cannot be undone. Please proceed with caution.

Download the latest version from our website. Installation instructions are included.""",
        "expected": {
            "query_answer": {"min": 5, "max": 25, "notes": "No context or specifics"},
            "llm_rubric": {"min": 10, "max": 30, "notes": "Lacks coherence and context"},
            "structure_quality": {"min": 15, "max": 35, "notes": "No heading, poor organization"},
            "entity_focus": {"min": 0, "max": 20, "notes": "No concrete entities"},
            "overall": {"min": 10, "max": 30}
        },
        "notes": "Scattered call-to-actions and warnings without context or heading"
    }
]