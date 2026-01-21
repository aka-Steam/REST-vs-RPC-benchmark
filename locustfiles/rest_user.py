"""
Locust load testing for REST API service.

This module defines the RestUser class for testing the REST API glossary service
using Locust's HttpUser.
"""
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from locust import HttpUser, task, between
from locustfiles.common import (
    get_rest_service_url,
    generate_term_data,
    extract_keywords_from_response,
    get_random_keyword,
    TASK_WEIGHT_LIST,
    TASK_WEIGHT_GET,
    TASK_WEIGHT_CREATE,
    WAIT_TIME_MIN,
    WAIT_TIME_MAX
)


class RestUser(HttpUser):
    """
    Locust user class for testing REST API service.
    
    Simulates realistic user behavior:
    - 50% of requests: List all terms (lightweight read operation)
    - 30% of requests: Get specific term (lightweight read operation)
    - 20% of requests: Create new term (write operation with DB commit)
    
    Wait time between requests: 1-3 seconds (realistic user behavior)
    """
    
    # Base URL for REST service (from environment or default)
    host = get_rest_service_url()
    
    # Wait time between requests (realistic user behavior)
    wait_time = between(WAIT_TIME_MIN, WAIT_TIME_MAX)
    
    def on_start(self):
        """
        Called when a user starts. Loads existing terms for use in tests.
        """
        # Load list of existing terms to use in GET requests
        try:
            response = self.client.get("/terms", name="[Setup] List Terms")
            if response.status_code == 200:
                terms_data = response.json()
                self.terms = extract_keywords_from_response(terms_data)
            else:
                self.terms = []
        except Exception as e:
            # If service is not available, start with empty list
            self.terms = []
    
    @task(TASK_WEIGHT_LIST)
    def task_list_terms(self):
        """
        Task: Get list of all terms.
        
        This is a lightweight read operation (SELECT all from database).
        Weight: 5 (50% probability)
        """
        response = self.client.get("/terms", name="List Terms")
        
        # Update terms list if request was successful
        if response.status_code == 200:
            try:
                terms_data = response.json()
                self.terms = extract_keywords_from_response(terms_data)
            except Exception:
                # Ignore JSON parsing errors, keep existing list
                pass
    
    @task(TASK_WEIGHT_GET)
    def task_get_term(self):
        """
        Task: Get a specific term by keyword.
        
        This is a lightweight read operation (SELECT with WHERE clause).
        Weight: 3 (30% probability)
        
        Uses a random keyword from the list loaded in on_start().
        If no terms are available, this task is skipped.
        """
        if not self.terms:
            # No terms available, skip this task
            return
        
        keyword = get_random_keyword(self.terms)
        if not keyword:
            return
        
        response = self.client.get(f"/terms/{keyword}", name="Get Term")
        
        # Handle 404 errors gracefully (term might have been deleted)
        if response.status_code == 404:
            # Remove from list if not found
            if keyword in self.terms:
                self.terms.remove(keyword)
    
    @task(TASK_WEIGHT_CREATE)
    def task_create_term(self):
        """
        Task: Create a new term.
        
        This is a write operation (SELECT check + INSERT + COMMIT).
        Weight: 2 (20% probability)
        
        Generates unique keyword to avoid conflicts.
        """
        # Generate unique term data
        term_data = generate_term_data()
        
        response = self.client.post(
            "/terms",
            json=term_data,
            name="Create Term"
        )
        
        # Handle different response codes
        if response.status_code == 201:
            # Successfully created, add to terms list
            try:
                created_term = response.json()
                if "keyword" in created_term:
                    if created_term["keyword"] not in self.terms:
                        self.terms.append(created_term["keyword"])
            except Exception:
                # Ignore JSON parsing errors
                pass
        elif response.status_code == 409:
            # Conflict - term already exists (expected in concurrent scenarios)
            # This is not an error, just a retry scenario
            pass
        # Other status codes (400, 500, etc.) will be tracked by Locust as errors
