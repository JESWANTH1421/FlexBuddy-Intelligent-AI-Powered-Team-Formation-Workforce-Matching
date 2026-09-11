"""
FlexBuddy - Mock Data
Employee database and preset project templates.
"""

# ---------------------------------------------------------------------------
# EMPLOYEE DATABASE (10 mock employees)
# ---------------------------------------------------------------------------
# skills: dict of skill_name -> proficiency (1-5)
# interests: list of tags
# availability: % free time employee has generally (0-100)
# workload: % of current capacity already committed (0-100)
# location: city

EMPLOYEES = [
    {
        "name": "Arun",
        "role": "AI/NLP Engineer",
        "skills": {"Python": 5, "NLP": 5, "FastAPI": 4, "SQL": 3, "AWS": 3},
        "interests": ["NLP", "GenAI", "LLM"],
        "availability": 80,
        "workload": 30,
        "location": "Chennai",
    },
    {
        "name": "Priya",
        "role": "Backend Developer",
        "skills": {"Python": 4, "React": 4, "SQL": 5, "FastAPI": 3, "AWS": 2},
        "interests": ["Backend", "Web", "APIs"],
        "availability": 70,
        "workload": 40,
        "location": "Chennai",
    },
    {
        "name": "Vishnu",
        "role": "Cloud Engineer",
        "skills": {"AWS": 5, "Docker": 4, "Python": 3, "SQL": 3, "CI/CD": 4},
        "interests": ["Cloud", "DevOps"],
        "availability": 90,
        "workload": 20,
        "location": "Bangalore",
    },
    {
        "name": "Divya",
        "role": "Frontend Developer",
        "skills": {"React": 5, "JavaScript": 5, "CSS": 4, "Python": 2, "UX": 3},
        "interests": ["UI/UX", "Frontend"],
        "availability": 60,
        "workload": 50,
        "location": "Chennai",
    },
    {
        "name": "Karthik",
        "role": "Data Engineer",
        "skills": {"Python": 4, "SQL": 5, "ETL": 4, "AWS": 3, "Spark": 3},
        "interests": ["Data Engineering", "BigData"],
        "availability": 75,
        "workload": 25,
        "location": "Bangalore",
    },
    {
        "name": "Meena",
        "role": "QA Engineer",
        "skills": {"Testing": 5, "Python": 3, "Selenium": 4, "SQL": 3, "CI/CD": 3},
        "interests": ["Automation", "QA"],
        "availability": 85,
        "workload": 15,
        "location": "Chennai",
    },
    {
        "name": "Vijay",
        "role": "DevOps Engineer",
        "skills": {"AWS": 5, "Docker": 5, "Kubernetes": 4, "CI/CD": 5, "Python": 3},
        "interests": ["Cloud", "DevOps", "Infra"],
        "availability": 50,
        "workload": 60,
        "location": "Hyderabad",
    },
    {
        "name": "Sneha",
        "role": "ML Engineer",
        "skills": {"Python": 5, "NLP": 4, "MachineLearning": 5, "SQL": 3, "FastAPI": 3},
        "interests": ["AI", "ML", "NLP", "GenAI"],
        "availability": 65,
        "workload": 45,
        "location": "Chennai",
    },
    {
        "name": "Rahul",
        "role": "Backend Developer",
        "skills": {"Java": 4, "Python": 3, "SQL": 4, "FastAPI": 3, "AWS": 2},
        "interests": ["Backend", "APIs"],
        "availability": 70,
        "workload": 35,
        "location": "Pune",
    },
    {
        "name": "Anita",
        "role": "Fullstack Developer",
        "skills": {"Python": 3, "React": 3, "SQL": 3, "NLP": 2, "AWS": 2},
        "interests": ["FullStack", "Product"],
        "availability": 55,
        "workload": 55,
        "location": "Bangalore",
    },
]

# ---------------------------------------------------------------------------
# PROJECT PRESETS
# ---------------------------------------------------------------------------
# Each required skill: {required: proficiency(1-5), weight: points(sum=100), critical: bool}

CORE_SKILL_CATEGORIES = {
    "Python": "core", "Java": "core", "FastAPI": "core", "React": "core",
    "JavaScript": "core", "CSS": "core", "UX": "core",
    "NLP": "specialization", "MachineLearning": "specialization", "GenAI": "specialization",
    "AWS": "infra", "Docker": "infra", "Kubernetes": "infra", "CI/CD": "infra",
    "Testing": "quality", "Selenium": "quality",
    "SQL": "data", "ETL": "data", "Spark": "data",
}

# How much each phase amplifies / dampens each skill category's weight.
# Weights are renormalized back to their original total after this is applied,
# so this only shifts *which* skills matter more within a project, not the
# overall scale of scores.
PHASE_WEIGHT_MULTIPLIER = {
    "Planning": {"core": 1.0, "specialization": 1.3, "infra": 1.2, "quality": 0.6, "data": 1.2},
    "Development": {"core": 1.4, "specialization": 1.1, "infra": 0.8, "quality": 0.7, "data": 1.0},
    "Testing": {"core": 0.9, "specialization": 0.7, "infra": 0.8, "quality": 1.8, "data": 0.9},
    "Deployment": {"core": 0.7, "specialization": 0.6, "infra": 1.8, "quality": 1.0, "data": 0.8},
}

PROJECT_PRESETS = {
    "AI Recruitment Chatbot": {
        "description": "Build an AI-powered chatbot that screens and shortlists job candidates.",
        "phase": "Development",
        "skills": {
            "Python": {"required": 4, "weight": 30, "critical": True},
            "NLP": {"required": 4, "weight": 25, "critical": True},
            "FastAPI": {"required": 3, "weight": 20, "critical": False},
            "SQL": {"required": 3, "weight": 15, "critical": False},
            "AWS": {"required": 3, "weight": 10, "critical": False},
        },
        "interests": ["NLP", "GenAI", "LLM", "AI"],
        "location": "Chennai",
        "team_size": 3,
        "workload": 50,
    },
    "Cloud Migration Platform": {
        "description": "Migrate on-prem services to a containerized cloud infrastructure.",
        "phase": "Planning",
        "skills": {
            "AWS": {"required": 4, "weight": 35, "critical": True},
            "Docker": {"required": 4, "weight": 25, "critical": True},
            "CI/CD": {"required": 3, "weight": 20, "critical": False},
            "Python": {"required": 2, "weight": 10, "critical": False},
            "Kubernetes": {"required": 3, "weight": 10, "critical": False},
        },
        "interests": ["Cloud", "DevOps", "Infra"],
        "location": "Bangalore",
        "team_size": 3,
        "workload": 40,
    },
    "Internal QA Automation Tool": {
        "description": "Build an automated regression testing suite for internal tools.",
        "phase": "Development",
        "skills": {
            "Testing": {"required": 4, "weight": 30, "critical": True},
            "Selenium": {"required": 3, "weight": 25, "critical": False},
            "Python": {"required": 3, "weight": 25, "critical": True},
            "SQL": {"required": 2, "weight": 10, "critical": False},
            "CI/CD": {"required": 2, "weight": 10, "critical": False},
        },
        "interests": ["Automation", "QA"],
        "location": "Chennai",
        "team_size": 2,
        "workload": 35,
    },
}