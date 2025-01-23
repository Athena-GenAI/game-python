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

@pytest.fixture
def mock_api():
    """Fixture to mock API responses."""
    with responses.RequestsMock() as rsps:
        # Mock authentication endpoint
        rsps.add(
            responses.POST,
            f"{config.api_url}/accesses/tokens",
            json={"data": {"accessToken": "test_token"}},
            status=200
        )
        yield rsps

def test_authentication_error():
    """Test handling of authentication errors."""
    with pytest.raises(AuthenticationError) as exc_info:
        Agent(
            api_key=INVALID_API_KEY,
            name="Test Agent",
            agent_description="Test Description",
            agent_goal="Test Goal",
            get_agent_state_fn=lambda x, y: {"status": "ready"}
        )
    assert "Invalid API key" in str(exc_info.value)

def test_validation_error():
    """Test handling of validation errors."""
    with pytest.raises(ValidationError) as exc_info:
        Agent(
            api_key=VALID_API_KEY,
            name="",  # Empty name should fail validation
            agent_description="Test Description",
            agent_goal="Test Goal",
            get_agent_state_fn=lambda x, y: {"status": "ready"}
        )
    assert "name" in str(exc_info.value).lower()

def test_network_error(mock_api):
    """Test handling of network errors."""
    with patch('requests.post') as mock_post:
        # Simulate connection error
        mock_post.side_effect = ConnectionError("Failed to connect")
        
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
        mock_post.side_effect = Timeout("Request timed out")
        
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
    mock_api.add(
        responses.POST,
        f"{config.api_url}/agents",
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
    # Mock invalid JSON response
    mock_api.add(
        responses.POST,
        f"{config.api_url}/agents",
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
    assert "invalid json" in str(exc_info.value).lower()

def test_server_error(mock_api):
    """Test handling of server errors."""
    # Mock server error
    mock_api.add(
        responses.POST,
        f"{config.api_url}/agents",
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
    assert exc_info.value.status_code == 500

def test_invalid_state_function():
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
    assert "dictionary" in str(exc_info.value).lower()

def test_empty_response_handling(mock_api):
    """Test handling of empty API responses."""
    # Mock empty response
    mock_api.add(
        responses.POST,
        f"{config.api_url}/agents",
        body="",
        status=204
    )
    
    # This should not raise an error
    agent = Agent(
        api_key=VALID_API_KEY,
        name="Test Agent",
        agent_description="Test Description",
        agent_goal="Test Goal",
        get_agent_state_fn=lambda x, y: {"status": "ready"}
    )
    assert agent is not None
