from __future__ import annotations

from prometheus_client import CollectorRegistry, Counter, Histogram

# Dedicated registry to avoid default collectors unless needed later.
metrics_registry = CollectorRegistry()

# Total requests by method/path/status
http_requests_total = Counter(
    "app_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
    registry=metrics_registry,
)

# Request duration histogram in seconds by method/path/status
http_request_duration_seconds = Histogram(
    "app_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path", "status"],
    buckets=(
        0.01,
        0.025,
        0.05,
        0.1,
        0.25,
        0.5,
        1,
        2.5,
        5,
        10,
    ),
    registry=metrics_registry,
)

# Backup job metrics
backup_jobs_total = Counter(
    "backup_jobs_total",
    "Total backup jobs by status",
    ["status"],
    registry=metrics_registry,
)

backup_job_retries_total = Counter(
    "backup_job_retries_total",
    "Total backup job retries",
    ["status"],
    registry=metrics_registry,
)

backup_job_duration_seconds = Histogram(
    "backup_job_duration_seconds",
    "Backup job duration in seconds",
    ["status"],
    buckets=(5, 10, 30, 60, 120, 300, 600, 1200, 1800),
    registry=metrics_registry,
)
