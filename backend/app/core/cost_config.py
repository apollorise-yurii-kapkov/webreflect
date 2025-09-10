"""
Cost configuration for tracking operational expenses.
Update these values based on actual service pricing.
"""

# OpenAI API Pricing (per token)
OPENAI_COSTS = {
    "gpt-5-nano": {
        "input": 0.00000005,   # $0.05 per 1M tokens
        "cached_input": 0.000000005,  # $0.005 per 1M tokens  
        "output": 0.0000004,   # $0.40 per 1M tokens
    },
    "gpt-5-mini": {
        "input": 0.00000025,   # $0.25 per 1M tokens
        "cached_input": 0.000000025,  # $0.025 per 1M tokens
        "output": 0.000002,    # $2.00 per 1M tokens
    },
    "gpt-4": {
        "input": 0.00000003,   # $0.03 per 1M tokens (converted from per 1K)
        "output": 0.00000006,  # $0.06 per 1M tokens (converted from per 1K)
    },
    "gpt-4-turbo": {
        "input": 0.00000001,   # $0.01 per 1M tokens (converted from per 1K)
        "output": 0.00000003,  # $0.03 per 1M tokens (converted from per 1K)
    },
    "gpt-3.5-turbo": {
        "input": 0.0000005, # $0.50 per 1M tokens
        "output": 0.0000015, # $1.50 per 1M tokens
    }
}

# Primary model configuration
PRIMARY_MODEL = "gpt-5-nano"

# Crawling costs (httpx + BeautifulSoup - no tokens used)
CRAWLING_COSTS = {
    "cost_per_page": 0.0,    # $0.00 - httpx requests are free
    "cost_per_mb": 0.0,      # $0.00 - BeautifulSoup parsing is free
    "bandwidth_cost": 0.0001, # $0.0001 per MB of bandwidth (optional)
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
