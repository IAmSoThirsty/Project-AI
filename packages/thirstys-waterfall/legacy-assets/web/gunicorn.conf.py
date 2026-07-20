"""
Gunicorn Production Configuration for Thirstys-Waterfall Web Interface
========================================================================

This configuration optimizes the web server for production deployment with
support for concurrent users, WebSocket connections, and high availability.

Configuration Philosophy:
-------------------------
1. Worker Count: (2 × CPU cores) + 1 for optimal throughput
2. Worker Class: gevent for async I/O and WebSocket support
3. Timeouts: Generous for long-polling/WebSocket connections
4. Graceful Restarts: Zero-downtime deployments
5. Resource Limits: Prevent memory leaks with max requests per worker
"""

import multiprocessing
import os

# =============================================================================
# SERVER SOCKET
# =============================================================================

bind = f"0.0.0.0:{os.getenv('WEB_PORT', '8080')}"
backlog = 2048  # Maximum pending connections

# =============================================================================
# WORKER PROCESSES
# =============================================================================

# Calculate optimal worker count: (2 × CPU cores) + 1
# Can be overridden with WORKERS environment variable
workers = int(os.getenv("WORKERS", multiprocessing.cpu_count() * 2 + 1))

# Worker class for async/WebSocket support
# 'gevent' provides greenlet-based concurrency for SocketIO
worker_class = os.getenv("WORKER_CLASS", "gevent")

# Worker connections (for gevent/eventlet workers)
worker_connections = 1000

# Maximum requests a worker will process before restarting
# Prevents memory leaks from accumulating
max_requests = 1000
max_requests_jitter = (
    50  # Add randomness to prevent all workers restarting simultaneously
)

# Worker timeout (seconds)
# Set high for WebSocket long-polling connections
timeout = 120

# Graceful timeout (seconds)
# Time to wait for workers to finish processing before force-killing
graceful_timeout = 30

# Keep-alive timeout (seconds)
keepalive = 5

# =============================================================================
# APPLICATION
# =============================================================================

# Preload application code before worker processes are forked
# Faster worker spawn time, but requires graceful reload for code changes
preload_app = True

# =============================================================================
# LOGGING
# =============================================================================

# Log level
loglevel = os.getenv("LOG_LEVEL", "info")

# Access log format
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Log files (use '-' for stdout/stderr)
accesslog = os.getenv("ACCESS_LOG", "-")
errorlog = os.getenv("ERROR_LOG", "-")

# Capture stdout/stderr in log
capture_output = True

# =============================================================================
# PROCESS NAMING
# =============================================================================

proc_name = "thirstys-waterfall-web"

# =============================================================================
# SERVER MECHANICS
# =============================================================================

# Daemonize the Gunicorn process (False for Docker)
daemon = False

# Process ID file location
pidfile = None

# User/group to run workers as (None = current user)
user = None
group = None

# Directory to change to before loading apps
chdir = "/app/web"

# Restart workers when code changes (development only)
reload = os.getenv("DEBUG", "False").lower() == "true"

# =============================================================================
# SERVER HOOKS
# =============================================================================


def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting Thirstys-Waterfall Web Interface")
    server.log.info(f"Workers: {workers} ({worker_class})")
    server.log.info(f"Binding to: {bind}")


def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("Reloading workers...")


def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Server is ready. Spawning workers")


def worker_int(worker):
    """Called when a worker receives the SIGINT or SIGQUIT signal."""
    worker.log.info("Worker received INT or QUIT signal")


def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")


def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass


def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info(f"Worker spawned (pid: {worker.pid})")


def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("Worker initialized")


def worker_exit(server, worker):
    """Called just after a worker has been exited."""
    server.log.info(f"Worker exited (pid: {worker.pid})")


def child_exit(server, worker):
    """Called just after a worker has been reaped."""
    pass


def on_exit(server):
    """Called just before exiting Gunicorn."""
    server.log.info("Shutting down Thirstys-Waterfall Web Interface")
