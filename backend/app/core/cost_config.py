"""
Cost configuration for tracking operational expenses.
Update these values based on actual service pricing.
"""

# OpenAI API Pricing (per token)
OPENAI_COSTS = {
    "gpt-5-nano": {
        "input": 0.00005,   # $0.050 per 1M tokens
        "cached_input": 0.000005,  # $0.005 per 1M tokens
        "output": 0.0004,   # $0.400 per 1M tokens
    },
    "gpt-5-mini": {
        "input": 0.00025,   # $0.250 per 1M tokens
        "cached_input": 0.000025,  # $0.025 per 1M tokens
        "output": 0.002,    # $2.000 per 1M tokens
    },
    "gpt-4": {
        "input": 0.00003,   # $0.03 per 1K tokens
        "output": 0.00006,  # $0.06 per 1K tokens
    },
    "gpt-4-turbo": {
        "input": 0.00001,   # $0.01 per 1K tokens  
        "output": 0.00003,  # $0.03 per 1K tokens
    },
    "gpt-3.5-turbo": {
        "input": 0.0000005, # $0.50 per 1M tokens
        "output": 0.0000015, # $1.50 per 1M tokens
    }
}

# Primary model configuration
PRIMARY_MODEL = "gpt-5-nano"

# Crawling costs (estimated)
CRAWLING_COSTS = {
    "cost_per_page": 0.001,  # $0.001 per page crawled
    "cost_per_mb": 0.01,     # $0.01 per MB of data
}

# Infrastructure costs (daily estimates)
INFRASTRUCTURE_COSTS = {
    "redis": 0.50,      # $0.50 per day
    "postgres": 1.00,   # $1.00 per day  
    "server": 5.00,     # $5.00 per day
}

# Cost thresholds for alerts
COST_ALERTS = {
    "daily_threshold": 10.00,    # Alert if daily costs exceed $10
    "monthly_threshold": 200.00, # Alert if monthly costs exceed $200
    "per_job_threshold": 1.00,   # Alert if single job costs exceed $1
}
