"""
Examples of error handling patterns in the GAME SDK.

This script demonstrates various error handling scenarios and best practices
when working with the GAME SDK.
"""

import logging
from typing import Optional, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential

from game_sdk.game.agent import Agent
from game_sdk.game.exceptions import (
    APIError,
    AuthenticationError,
    ValidationError
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handle_authentication_error(api_key: str) -> Optional[str]:
    """Example of handling authentication errors."""
    try:
        agent = Agent(
            api_key=api_key,
            name="Test Agent",
            agent_description="Testing auth errors",
            agent_goal="Demonstrate error handling",
            get_agent_state_fn=lambda x, y: {"status": "ready"}
        )
        return agent.agent_id
    except AuthenticationError as e:
        if e.status_code == 401:
            logger.error("Invalid API key. Please check your credentials.")
        elif e.status_code == 403:
            logger.error("API key lacks necessary permissions.")
        else:
            logger.error(f"Authentication failed: {e}")
        return None


def handle_validation_error(agent_config: Dict[str, Any]) -> Optional[str]:
    """Example of handling validation errors."""
    try:
        agent = Agent(
            api_key=agent_config.get("api_key", ""),
            name=agent_config.get("name", ""),
            agent_description=agent_config.get("description", ""),
            agent_goal=agent_config.get("goal", ""),
            get_agent_state_fn=lambda x, y: {"status": "ready"}
        )
        return agent.agent_id
    except ValidationError as e:
        logger.error(f"Invalid agent configuration: {e}")
        # Log detailed validation errors
        if hasattr(e, 'errors'):
            for field, error in e.errors.items():
                logger.error(f"Field '{field}': {error}")
        return None


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def create_agent_with_retry(api_key: str, name: str, description: str, goal: str) -> Optional[str]:
    """Example of implementing retries for API calls."""
    try:
        agent = Agent(
            api_key=api_key,
            name=name,
            agent_description=description,
            agent_goal=goal,
            get_agent_state_fn=lambda x, y: {"status": "ready"}
        )
        return agent.agent_id
    except APIError as e:
        if e.status_code >= 500:  # Retry on server errors
            logger.warning(f"Server error (attempt {retry.statistics['attempt_number']})")
            raise  # This will trigger a retry
        else:
            logger.error(f"API error: {e}")
            raise e from None  # Don't retry on client errors


def demonstrate_error_handling():
    """Run through various error handling scenarios."""
    # 1. Authentication Error Example
    logger.info("Testing authentication error handling...")
    result = handle_authentication_error("invalid_api_key")
    if result is None:
        logger.info("Successfully handled authentication error")

    # 2. Validation Error Example
    logger.info("\nTesting validation error handling...")
    invalid_config = {
        "api_key": "valid_key",
        "name": "",  # Empty name should trigger validation error
        "description": "Test Description",
        "goal": "Test Goal"
    }
    result = handle_validation_error(invalid_config)
    if result is None:
        logger.info("Successfully handled validation error")

    # 3. Retry Example
    logger.info("\nTesting retry mechanism...")
    try:
        result = create_agent_with_retry(
            "valid_key",
            "Test Agent",
            "Testing retries",
            "Demonstrate retry mechanism"
        )
        logger.info("Successfully created agent with retry mechanism")
    except APIError as e:
        logger.error(f"Failed after retries: {e}")


if __name__ == "__main__":
    demonstrate_error_handling()
