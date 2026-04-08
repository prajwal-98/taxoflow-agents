# City-specific slang and operational signals for Q-Commerce grounding
CITY_SLANG_MAP = {
    "Bangalore": [
        "Potadi",      # Refers to bags/packets
        "Sakkath",     # High quality/Great
        "Bega",        # Fast/Quickly
        "Maga",        # Casual address
        "Guru"         # Addressing someone (delivery partner)
    ],
    "Mumbai": [
        "Lafda",       # Issue/Problem
        "Kadak",       # Excellent/Strong
        "Bantai",      # Casual address
        "Ek Number",   # Top tier quality
        "Chindi"       # Low quality/Small issues
    ],
    "Delhi": [
        "Bhasad",      # Chaos/Traffic/Confusion
        "Gajab",       # Amazing
        "Scene",       # Situation/Problem
        "Tashan",      # Style/Attitude
        "Vibe"         # Atmosphere
    ],
    "Hyderabad": [
        "Kaiku",       # Why (used in complaints)
        "Hau",         # Yes
        "Nakko",       # No/Don't want
        "Kirrak",      # Awesome
        "Ustad"        # Addressing someone expert
    ],
    "Pune": [
        "Lay Bhari",   # Very good
        "Kalti",       # To leave/avoid
        "Raav",        # Respectful address
        "Jakaas",      # Fantastic
        "Vishesh"      # Special/Specifically
    ]
}

# Standardized business categories for Agent 5
BUSINESS_CATEGORIES = [
    "Logistics",
    "Pricing",
    "Product Quality",
    "App Experience",
    "Customer Support"
]