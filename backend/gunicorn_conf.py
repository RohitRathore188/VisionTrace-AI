"""
Gunicorn Configuration for Production Deployment
Configures Uvicorn worker process pool, concurrency limits, and timeouts.
"""

import os
import multiprocessing

# Server socket settings
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
backlog = 2048

# Worker processes configuration
workers_per_core_str = os.getenv("WORKERS_PER_CORE", "1")
cores = multiprocessing.cpu_count()
default_web_concurrency = cores * float(workers_per_core_str)
workers = max(int(os.getenv("WEB_CONCURRENCY", default_web_concurrency)), 2)

worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 300  # Extended timeout for AI inference & video chunk uploads
keepalive = 5

# Logging settings
loglevel = os.getenv("LOG_LEVEL", "info")
accesslog = "-"
errorlog = "-"

# Memory management & restart policies
max_requests = 1000
max_requests_jitter = 50
