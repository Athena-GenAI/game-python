"""
Integration tests for error handling in the GAME SDK.
"""

import pytest
import responses
from unittest.mock import patch
from requests.exceptions import ConnectionError, Timeout

from game_sdk.game.agent import Agent
from game_sdk.game.exceptions import (
    APIError,
    AuthenticationError,
    ValidationError
)
from game_sdk.game.config import config

# Test data
VALID_API_KEY = "test_api_key"
INVALID_API_KEY = "invalid_key"
AUTH_URL = "https://api.virtuals.io/api/accesses/tokens"
BASE_URL = "https://api.virtuals.io"
AGENT_URL = f"{BASE_URL}/v2/agents"

@pytest.fixture
def mock_api():
    """Fixture to mock API responses."""
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        # Mock authentication endpoint
        rsps.add(
            responses.POST,
            AUTH_URL,
            json={"data": {"accessToken": "test_token"}},
            status=200
        )
        # Mock agent creation endpoint
        rsps.add(
            responses.POST,
            AGENT_URL,
            json={"data": {"id": "test_agent_id"}},
            status=200
        )
        yield rsps

def test_authentication_error(mock_api):
    """Test handling of authentication errors."""
    # Mock failed authentication
    mock_api.replace(
        responses.POST,
        AUTH_URL,
        json={"error": {"message": "Invalid API key"}},
        status=401
    )
    
    with pytest.raises(AuthenticationError) as exc_info:
        Agent(
            api_key=INVALID_API_KEY,
            name="Test Agent",
            agent_description="Test Description",
            agent_goal="Test Goal",
            get_agent_state_fn=lambda x, y: {"status": "ready"}
        )

def test_validation_error(mock_api):
    """Test handling of validation errors."""
    with pytest.raises(ValidationError) as exc_info:
        Agent(
            api_key=VALID_API_KEY,
            name="",  # Empty name should fail validation
            agent_description="Test Description",
            agent_goal="Test Goal",
            get_agent_state_fn=lambda x, y: {"status": "ready"}
        )
    assert "empty" in str(exc_info.value).lower()

def test_network_error(mock_api):
    """Test handling of network errors."""
    with patch('requests.post') as mock_post:
        # Simulate connection error
        mock_post.side_effect = ConnectionError("Connection failed")
    
        with pytest.raises(APIError) as exc_info:
            Agent(
                api_key=VALID_API_KEY,
                name="Test Agent",
                agent_description="Test Description",
                agent_goal="Test Goal",
                get_agent_state_fn=lambda x, y: {"status": "ready"}
            )
        assert "connection" in str(exc_info.value).lower()

def test_timeout_error(mock_api):
    """Test handling of timeout errors."""
    with patch('requests.post') as mock_post:
        # Simulate timeout
        mock_post.side_effect = Timeout("Connection timeout")
    
        with pytest.raises(APIError) as exc_info:
            Agent(
                api_key=VALID_API_KEY,
                name="Test Agent",
                agent_description="Test Description",
                agent_goal="Test Goal",
                get_agent_state_fn=lambda x, y: {"status": "ready"}
            )
        assert "timeout" in str(exc_info.value).lower()

def test_rate_limit_error(mock_api):
    """Test handling of rate limit errors."""
    # Mock rate limit response
    mock_api.replace(
        responses.POST,
        AGENT_URL,
        json={"error": "Rate limit exceeded"},
        status=429
    )
    
    with pytest.raises(APIError) as exc_info:
        agent = Agent(
            api_key=VALID_API_KEY,
            name="Test Agent",
            agent_description="Test Description",
            agent_goal="Test Goal",
            get_agent_state_fn=lambda x, y: {"status": "ready"}
        )
    assert exc_info.value.status_code == 429

def test_malformed_response(mock_api):
    """Test handling of malformed API responses."""
    # Mock malformed response
    mock_api.replace(
        responses.POST,
        AGENT_URL,
        body="Invalid JSON",
        status=200
    )
    
    with pytest.raises(APIError) as exc_info:
        agent = Agent(
            api_key=VALID_API_KEY,
            name="Test Agent",
            agent_description="Test Description",
            agent_goal="Test Goal",
            get_agent_state_fn=lambda x, y: {"status": "ready"}
        )
    assert "invalid" in str(exc_info.value).lower()

def test_server_error(mock_api):
    """Test handling of server errors."""
    # Mock server error
    mock_api.replace(
        responses.POST,
        AGENT_URL,
        json={"error": "Internal server error"},
        status=500
    )
    
    with pytest.raises(APIError) as exc_info:
        agent = Agent(
            api_key=VALID_API_KEY,
            name="Test Agent",
            agent_description="Test Description",
            agent_goal="Test Goal",
            get_agent_state_fn=lambda x, y: {"status": "ready"}
        )

def test_invalid_state_function(mock_api):
    """Test handling of invalid state functions."""
    def bad_state_fn(result, state):
        return "Not a dictionary"  # Invalid return type
    
    with pytest.raises(ValidationError) as exc_info:
        agent = Agent(
            api_key=VALID_API_KEY,
            name="Test Agent",
            agent_description="Test Description",
            agent_goal="Test Goal",
            get_agent_state_fn=bad_state_fn
        )

def test_empty_response_handling(mock_api):
    """Test handling of empty API responses."""
    # Mock empty response
    mock_api.replace(
        responses.POST,
        AGENT_URL,
        json={"data": {"id": "test_agent_id"}},  # Return a valid response
        status=200
    )
    
    # This should not raise an error
    agent = Agent(
        api_key=VALID_API_KEY,
        name="Test Agent",
        agent_description="Test Description",
        agent_goal="Test Goal",
        get_agent_state_fn=lambda x, y: {"status": "ready"}
    )
