"""
Locust load testing for gRPC service.

This module defines the GrpcUser class for testing the gRPC glossary service
using Locust's User class and gRPC client.
"""

import sys
import time
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Add glossary_RPCservice to path for protobuf imports
grpc_service_path = project_root / "glossary_RPCservice"
if str(grpc_service_path) not in sys.path:
    sys.path.insert(0, str(grpc_service_path))

import grpc
from locust import User, task, between, events
from locustfiles.common import (
    get_grpc_service_address,
    generate_term_data,
    get_random_keyword,
    TASK_WEIGHT_LIST,
    TASK_WEIGHT_GET,
    TASK_WEIGHT_CREATE,
    WAIT_TIME_MIN,
    WAIT_TIME_MAX
)

# Import protobuf generated files
import glossary_pb2 as pb
import glossary_pb2_grpc as rpc


def fire_request_event(name: str, response_time: float, response_length: int, exception: Exception = None):
    """
    Fire a Locust request event to record metrics for gRPC calls.
    
    Args:
        name: Name of the request (for grouping in statistics)
        response_time: Response time in milliseconds
        response_length: Response length in bytes (0 for gRPC as it's binary)
        exception: Exception if request failed, None otherwise
    """
    events.request.fire(
        request_type="gRPC",
        name=name,
        response_time=response_time,
        response_length=response_length,
        exception=exception,
        context={}
    )


class GrpcUser(User):
    """
    Locust user class for testing gRPC service.
    
    Simulates realistic user behavior:
    - 50% of requests: List all terms (lightweight read operation)
    - 30% of requests: Get specific term (lightweight read operation)
    - 20% of requests: Create new term (write operation with DB commit)
    
    Wait time between requests: 1-3 seconds (realistic user behavior)
    """
    
    # Wait time between requests (realistic user behavior)
    wait_time = between(WAIT_TIME_MIN, WAIT_TIME_MAX)
    
    def on_start(self):
        """
        Called when a user starts. Creates gRPC channel and loads existing terms.
        """
        # Create gRPC channel and stub
        self.address = get_grpc_service_address()
        self.channel = grpc.insecure_channel(self.address)
        self.stub = rpc.GlossaryServiceStub(self.channel)
        
        # Load list of existing terms to use in GET requests
        try:
            start_time = time.time()
            request = pb.ListTermsRequest()
            response = self.stub.ListTerms(request)
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Extract keywords from response
            self.terms = [item.keyword for item in response.items]
            
            # Record the setup request
            fire_request_event("[Setup] List Terms", response_time, 0)
        except Exception as e:
            # If service is not available, start with empty list
            self.terms = []
            fire_request_event("[Setup] List Terms", 0, 0, e)
    
    def on_stop(self):
        """
        Called when a user stops. Closes gRPC channel.
        """
        if hasattr(self, 'channel'):
            self.channel.close()
    
    @task(TASK_WEIGHT_LIST)
    def task_list_terms(self):
        """
        Task: Get list of all terms.
        
        This is a lightweight read operation (SELECT all from database).
        Weight: 5 (50% probability)
        """
        try:
            start_time = time.time()
            request = pb.ListTermsRequest()
            response = self.stub.ListTerms(request)
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Update terms list
            self.terms = [item.keyword for item in response.items]
            
            # Record successful request
            fire_request_event("List Terms", response_time, 0)
        except grpc.RpcError as e:
            response_time = (time.time() - start_time) * 1000
            fire_request_event("List Terms", response_time, 0, e)
        except Exception as e:
            response_time = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0
            fire_request_event("List Terms", response_time, 0, e)
    
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
        
        try:
            start_time = time.time()
            request = pb.GetTermRequest(keyword=keyword)
            response = self.stub.GetTerm(request)
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Record successful request
            fire_request_event("Get Term", response_time, 0)
        except grpc.RpcError as e:
            response_time = (time.time() - start_time) * 1000
            # Handle NOT_FOUND gracefully (term might have been deleted)
            if e.code() == grpc.StatusCode.NOT_FOUND:
                if keyword in self.terms:
                    self.terms.remove(keyword)
                # Still record as error for statistics
                fire_request_event("Get Term", response_time, 0, e)
            else:
                fire_request_event("Get Term", response_time, 0, e)
        except Exception as e:
            response_time = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0
            fire_request_event("Get Term", response_time, 0, e)
    
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
        
        try:
            start_time = time.time()
            request = pb.CreateTermRequest(
                item=pb.Term(
                    keyword=term_data["keyword"],
                    description=term_data["description"]
                )
            )
            response = self.stub.CreateTerm(request)
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Successfully created, add to terms list
            if response.item.keyword not in self.terms:
                self.terms.append(response.item.keyword)
            
            # Record successful request
            fire_request_event("Create Term", response_time, 0)
        except grpc.RpcError as e:
            response_time = (time.time() - start_time) * 1000
            # Handle ALREADY_EXISTS gracefully (expected in concurrent scenarios)
            if e.code() == grpc.StatusCode.ALREADY_EXISTS:
                # This is not a critical error, just a retry scenario
                # Still record for statistics
                fire_request_event("Create Term", response_time, 0, e)
            else:
                fire_request_event("Create Term", response_time, 0, e)
        except Exception as e:
            response_time = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0
            fire_request_event("Create Term", response_time, 0, e)

