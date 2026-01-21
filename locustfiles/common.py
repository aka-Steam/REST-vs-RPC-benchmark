"""
Common utilities for Locust load testing.

This module provides shared functions for generating test data,
loading configuration, and other utilities used by both REST and gRPC test classes.
"""

import os
import random
import string
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration constants
REST_SERVICE_URL = os.getenv("REST_SERVICE_URL", "http://localhost:8000")
GRPC_SERVICE_HOST = os.getenv("GRPC_SERVICE_HOST", "localhost")
GRPC_SERVICE_PORT = int(os.getenv("GRPC_SERVICE_PORT", "50051"))

# Sample keywords for generating test data
SAMPLE_KEYWORDS = [
    "API", "REST", "gRPC", "HTTP", "HTTPS", "JSON", "XML", "SOAP",
    "GraphQL", "WebSocket", "TCP", "UDP", "DNS", "SSL", "TLS",
    "OAuth", "JWT", "Bearer", "CORS", "Cache", "CDN", "LoadBalancer",
    "Microservice", "Monolith", "Container", "Docker", "Kubernetes",
    "CI", "CD", "DevOps", "Agile", "Scrum", "Sprint", "Backlog",
    "Database", "SQL", "NoSQL", "MongoDB", "PostgreSQL", "Redis",
    "Elasticsearch", "Kafka", "RabbitMQ", "MessageQueue", "EventBus",
    "Async", "Sync", "Thread", "Process", "Coroutine", "Promise",
    "Observable", "Stream", "Buffer", "Queue", "Stack", "Heap",
    "Algorithm", "DataStructure", "BigO", "Complexity", "Optimization",
    "Framework", "Library", "Package", "Module", "Dependency",
    "Repository", "Service", "Controller", "Middleware", "Handler",
    "Router", "Endpoint", "Route", "Path", "Query", "Parameter",
    "Request", "Response", "Header", "Body", "Payload", "Status",
    "Error", "Exception", "Logging", "Monitoring", "Metrics",
    "Performance", "Scalability", "Reliability", "Availability",
    "Security", "Authentication", "Authorization", "Encryption",
    "Hash", "Salt", "Token", "Session", "Cookie", "State"
]

# Sample descriptions (shorter versions for API responses)
SAMPLE_DESCRIPTIONS = [
    "Application Programming Interface",
    "Representational State Transfer",
    "gRPC Remote Procedure Calls",
    "HyperText Transfer Protocol",
    "Secure HTTP protocol",
    "JavaScript Object Notation",
    "eXtensible Markup Language",
    "Simple Object Access Protocol",
    "Graph Query Language",
    "WebSocket protocol",
    "Transmission Control Protocol",
    "User Datagram Protocol",
    "Domain Name System",
    "Secure Sockets Layer",
    "Transport Layer Security",
    "Open Authorization standard",
    "JSON Web Token",
    "Bearer token format",
    "Cross-Origin Resource Sharing",
    "Temporary data storage",
    "Content Delivery Network",
    "Load balancing mechanism",
    "Microservice architecture",
    "Monolithic architecture",
    "Application container",
    "Containerization platform",
    "Container orchestration",
    "Continuous Integration",
    "Continuous Deployment",
    "Development and Operations",
    "Agile methodology",
    "Project management framework",
    "Development sprint",
    "Task backlog",
    "Data storage system",
    "Structured Query Language",
    "Not Only SQL databases",
    "Document-oriented database",
    "Relational database system",
    "In-memory data store",
    "Search engine",
    "Stream processing platform",
    "Message broker",
    "Message queue system",
    "Event bus pattern",
    "Asynchronous execution",
    "Synchronous execution",
    "Execution thread",
    "Process execution",
    "Coroutine function",
    "Promise object",
    "Observable pattern",
    "Data stream",
    "Data buffer",
    "Queue data structure",
    "Stack data structure",
    "Heap data structure",
    "Algorithm implementation",
    "Data structure",
    "Big O notation",
    "Algorithm complexity",
    "Performance optimization",
    "Software framework",
    "Code library",
    "Software package",
    "Code module",
    "Dependency management",
    "Data repository",
    "Business service",
    "Request controller",
    "Middleware component",
    "Request handler",
    "Route router",
    "API endpoint",
    "URL route",
    "URL path",
    "Query parameter",
    "Function parameter",
    "HTTP request",
    "HTTP response",
    "HTTP header",
    "Request body",
    "Data payload",
    "Status code",
    "Error condition",
    "Exception handling",
    "Logging system",
    "System monitoring",
    "Performance metrics",
    "System performance",
    "System scalability",
    "System reliability",
    "System availability",
    "Security measures",
    "User authentication",
    "Access authorization",
    "Data encryption",
    "Hash function",
    "Password salt",
    "Access token",
    "User session",
    "Browser cookie",
    "Application state"
]


def generate_keyword(prefix: Optional[str] = None, suffix_length: int = 6) -> str:
    """
    Generate a unique keyword for testing.
    
    Args:
        prefix: Optional prefix for the keyword. If None, uses random sample keyword.
        suffix_length: Length of random suffix to ensure uniqueness.
    
    Returns:
        A unique keyword string.
    """
    if prefix is None:
        base = random.choice(SAMPLE_KEYWORDS)
    else:
        base = prefix
    
    # Add random suffix to ensure uniqueness
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=suffix_length))
    return f"{base}_{suffix}"


def generate_description(keyword: Optional[str] = None) -> str:
    """
    Generate a test description.
    
    Args:
        keyword: Optional keyword to match description to.
    
    Returns:
        A description string.
    """
    if keyword:
        # Try to match description to keyword
        keyword_upper = keyword.upper()
        for i, kw in enumerate(SAMPLE_KEYWORDS):
            if kw.upper() in keyword_upper:
                if i < len(SAMPLE_DESCRIPTIONS):
                    return SAMPLE_DESCRIPTIONS[i]
    
    # Fallback to random description
    return random.choice(SAMPLE_DESCRIPTIONS)


def generate_term_data() -> dict:
    """
    Generate a complete term data dictionary for API requests.
    
    Returns:
        Dictionary with 'keyword' and 'description' keys.
    """
    keyword = generate_keyword()
    description = generate_description(keyword)
    return {
        "keyword": keyword,
        "description": description
    }


def get_rest_service_url() -> str:
    """Get REST service URL from environment or default."""
    return REST_SERVICE_URL


def get_grpc_service_host() -> str:
    """Get gRPC service host from environment or default."""
    return GRPC_SERVICE_HOST


def get_grpc_service_port() -> int:
    """Get gRPC service port from environment or default."""
    return GRPC_SERVICE_PORT


def get_grpc_service_address() -> str:
    """Get full gRPC service address (host:port)."""
    return f"{GRPC_SERVICE_HOST}:{GRPC_SERVICE_PORT}"


def extract_keywords_from_response(response_data: List[dict]) -> List[str]:
    """
    Extract keywords from API response data.
    
    Args:
        response_data: List of dictionaries from API response (e.g., from GET /terms).
    
    Returns:
        List of keyword strings.
    """
    if not response_data:
        return []
    
    keywords = []
    for item in response_data:
        if isinstance(item, dict) and "keyword" in item:
            keywords.append(item["keyword"])
        elif hasattr(item, "keyword"):
            keywords.append(item.keyword)
    
    return keywords


def get_random_keyword(keywords: List[str]) -> Optional[str]:
    """
    Get a random keyword from a list.
    
    Args:
        keywords: List of keyword strings.
    
    Returns:
        Random keyword or None if list is empty.
    """
    if not keywords:
        return None
    return random.choice(keywords)


def create_unique_keyword(existing_keywords: set, base: Optional[str] = None) -> str:
    """
    Create a unique keyword that doesn't exist in the provided set.
    
    Args:
        existing_keywords: Set of existing keywords to avoid.
        base: Optional base keyword. If None, generates random base.
    
    Returns:
        A unique keyword string.
    """
    max_attempts = 100
    for _ in range(max_attempts):
        keyword = generate_keyword(prefix=base)
        if keyword not in existing_keywords:
            return keyword
    
    # Fallback: use timestamp-based keyword
    import time
    timestamp = int(time.time() * 1000)
    keyword = f"TERM_{timestamp}_{random.randint(1000, 9999)}"
    return keyword


# Task weight constants for Locust tasks
TASK_WEIGHT_LIST = 5      # 50% probability (5 out of 10)
TASK_WEIGHT_GET = 3       # 30% probability (3 out of 10)
TASK_WEIGHT_CREATE = 2    # 20% probability (2 out of 10)

# Wait time configuration
WAIT_TIME_MIN = 1  # Minimum seconds between requests
WAIT_TIME_MAX = 3  # Maximum seconds between requests

