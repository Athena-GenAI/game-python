import requests
from typing import List, Dict, Any
from requests.exceptions import ConnectionError, Timeout, JSONDecodeError
from game_sdk.game.exceptions import AuthenticationError, ValidationError, APIError


def get_access_token(api_key) -> str:
    """
    API call to get access token
    """
    try:
        response = requests.post(
            "https://api.virtuals.io/api/accesses/tokens",
            json={"data": {}},
            headers={"x-api-key": api_key}
        )
    except (ConnectionError, Timeout) as e:
        raise APIError(f"Connection failed: {str(e)}")

    try:
        response_json = response.json()
    except JSONDecodeError:
        raise APIError("Invalid JSON response")

    if response.status_code == 401:
        raise AuthenticationError("Invalid API key")
    elif response.status_code != 200:
        raise APIError(f"Failed to get token: {response_json}", response.status_code)

    return response_json["data"]["accessToken"]


def post(base_url: str, api_key: str, endpoint: str, data: dict) -> Dict[str, Any]:
    """
    API call to post data
    """
    try:
        access_token = get_access_token(api_key)
    except (ConnectionError, Timeout) as e:
        raise APIError(f"Connection failed: {str(e)}")

    try:
        response = requests.post(
            f"{base_url}{endpoint}",
            json=data,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )
    except (ConnectionError, Timeout) as e:
        raise APIError(f"Connection failed: {str(e)}")

    try:
        response_json = response.json()
    except JSONDecodeError:
        if response.status_code == 204:
            return {}  # Return empty dict for 204 No Content
        raise APIError("Invalid JSON response")

    if response.status_code == 400:
        error_msg = response_json.get("error", {}).get("message", "Invalid request")
        raise ValidationError(error_msg)
    elif response.status_code == 429:
        raise APIError("Rate limit exceeded", response.status_code)
    elif response.status_code >= 500:
        raise APIError("Server error", response.status_code)
    elif response.status_code != 200:
        raise APIError(f"Failed to post data: {response_json}", response.status_code)

    return response_json.get("data", {})


def create_agent(
        base_url: str,
        api_key: str,
        name: str,
        description: str,
        goal: str) -> str:
    """
    API call to create an agent instance (worker or agent with task generator)
    """
    if not isinstance(name, str) or not name.strip():
        raise ValidationError("Name cannot be empty")

    create_agent_response = post(
        base_url,
        api_key,
        endpoint="/v2/agents",
        data={
            "name": name,
            "description": description,
            "goal": goal,
        }
    )

    agent_id = create_agent_response.get("id")
    if not agent_id:
        raise APIError("Failed to create agent: missing id in response")

    return agent_id


def create_workers(base_url: str,
                   api_key: str,
                   workers: List) -> str:
    """
    API call to create workers and worker description for the task generator
    """
    workers_data = []
    for worker in workers:
        workers_data.append({
            "id": worker.id,
            "description": worker.worker_description,
            "instruction": worker.instruction,
            "action_space": [f.get_function_def() for f in worker.action_space.values()]
        })

    create_workers_response = post(
        base_url,
        api_key,
        endpoint="/v2/workers",
        data={"workers": workers_data}
    )

    worker_id = create_workers_response.get("id")
    if not worker_id:
        raise APIError("Failed to create workers: missing id in response")

    return worker_id
