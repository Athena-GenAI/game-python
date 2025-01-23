"""
Example of creating and testing a Weather Reporter worker.

This script demonstrates how to create and test a worker that provides
weather information and recommendations.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

from game_sdk.game.agent import Agent
from game_sdk.game.exceptions import ValidationError, APIError

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_weather_reporter(api_key: str) -> Tuple[Optional[Any], Optional[Dict[str, Any]]]:
    """
    Create a weather reporter worker.
    
    Args:
        api_key: Your API key
    
    Returns:
        Tuple containing (worker, config) if successful, (None, None) otherwise
    """
    try:
        # Create an agent to manage our worker
        agent = Agent(
            api_key=api_key,
            name="Weather Assistant",
            agent_description="An AI that reports weather and gives recommendations",
            agent_goal="Help users make weather-informed decisions",
            get_agent_state_fn=lambda x, y: {"status": "ready"}
        )

        # Define the worker configuration
        worker_config = {
            "id": f"weather_reporter_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "description": "A smart weather reporting and recommendation system",
            "instruction": """
                This worker can:
                1. Report current weather conditions
                2. Provide clothing recommendations
                3. Suggest activities based on weather
                4. Track weather history
            """,
            "action_space": [
                {
                    "name": "get_weather",
                    "description": "Get current weather conditions",
                    "parameters": {
                        "location": {
                            "type": "string",
                            "description": "City name or zip code"
                        }
                    }
                },
                {
                    "name": "get_clothing_recommendation",
                    "description": "Get clothing recommendations for current weather",
                    "parameters": {
                        "location": {
                            "type": "string",
                            "description": "City name or zip code"
                        },
                        "activity": {
                            "type": "string",
                            "description": "Planned activity (e.g., 'outdoor sports', 'casual walk')",
                            "optional": True
                        }
                    }
                },
                {
                    "name": "suggest_activities",
                    "description": "Get activity suggestions based on weather",
                    "parameters": {
                        "location": {
                            "type": "string",
                            "description": "City name or zip code"
                        },
                        "preference": {
                            "type": "string",
                            "description": "Preferred type (indoor/outdoor)",
                            "enum": ["indoor", "outdoor", "both"]
                        }
                    }
                },
                {
                    "name": "get_weather_history",
                    "description": "Get weather history for a location",
                    "parameters": {
                        "location": {
                            "type": "string",
                            "description": "City name or zip code"
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of days of history",
                            "minimum": 1,
                            "maximum": 7
                        }
                    }
                }
            ]
        }

        # Create the worker
        worker = agent.create_worker(worker_config)
        logger.info(f"Created weather reporter worker with ID: {worker_config['id']}")
        return worker, worker_config

    except Exception as e:
        logger.error(f"Failed to create weather reporter: {e}")
        return None, None

def test_weather_reporter(worker: Any, config: Dict[str, Any]) -> bool:
    """
    Run tests on the weather reporter worker.
    
    Args:
        worker: Worker instance to test
        config: Worker configuration dictionary
    
    Returns:
        bool: True if all tests pass, False otherwise
    """
    test_cases = [
        # Test weather reporting
        {
            "action": "get_weather",
            "parameters": {
                "location": "New York, NY"
            },
            "description": "Getting weather for New York"
        },
        # Test clothing recommendations
        {
            "action": "get_clothing_recommendation",
            "parameters": {
                "location": "Miami, FL",
                "activity": "beach day"
            },
            "description": "Getting clothing recommendations for Miami beach day"
        },
        # Test activity suggestions
        {
            "action": "suggest_activities",
            "parameters": {
                "location": "Seattle, WA",
                "preference": "both"
            },
            "description": "Getting activity suggestions for Seattle"
        },
        # Test weather history
        {
            "action": "get_weather_history",
            "parameters": {
                "location": "Boston, MA",
                "days": 3
            },
            "description": "Getting weather history for Boston"
        }
    ]

    for test in test_cases:
        try:
            logger.info(f"\nExecuting: {test['description']}")
            result = worker.execute_action(
                test["action"],
                test["parameters"]
            )
            logger.info(f"Result: {result}")
            logger.info("✓ Test passed")

        except Exception as e:
            logger.error(f"Test failed: {e}")
            return False

    return True

def main():
    """Run the weather reporter example."""
    # Replace with your API key
    api_key = "your_api_key_here"

    # Create the weather reporter
    worker, config = create_weather_reporter(api_key)
    if not worker:
        logger.error("Failed to create weather reporter")
        return

    # Test the worker
    success = test_weather_reporter(worker, config)
    if success:
        logger.info("\n✨ All weather reporter tests passed!")
    else:
        logger.error("\n❌ Some weather reporter tests failed")

if __name__ == "__main__":
    main()
