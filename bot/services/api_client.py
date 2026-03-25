"""LMS API client.

This module handles all HTTP requests to the LMS backend.
It uses Bearer token authentication and provides user-friendly error messages.
"""

import httpx
from config import config


class APIError(Exception):
    """Exception raised when the API request fails.

    Contains a user-friendly error message that includes the actual error.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class LMSAPI:
    """Client for the LMS backend API.

    All methods make HTTP requests to the backend and return parsed responses.
    Errors are caught and converted to user-friendly messages.
    """

    def __init__(self):
        self.base_url = config.lms_api_base_url.rstrip("/")
        self.api_key = config.lms_api_key
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def _get(self, endpoint: str, params: dict | None = None) -> dict | list:
        """Make a GET request to the API.

        Args:
            endpoint: API endpoint path, e.g., "/items/"
            params: Optional query parameters

        Returns:
            Parsed JSON response

        Raises:
            APIError: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        try:
            with httpx.Client() as client:
                response = client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise APIError(f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down.")
        except httpx.ConnectError as e:
            # Extract the core error message from the exception
            error_msg = str(e)
            if "connection refused" in error_msg.lower():
                raise APIError("Connection refused. Check that the backend services are running.")
            elif "111" in error_msg:
                raise APIError("Connection refused (localhost:42002). Check that the services are running.")
            else:
                raise APIError(f"Connection error: {error_msg}")
        except Exception as e:
            raise APIError(f"Unexpected error: {str(e)}")

    def post(self, endpoint: str, json: dict | None = None) -> dict | list:
        """Make a POST request to the API.

        Args:
            endpoint: API endpoint path, e.g., "/pipeline/sync"
            json: Optional JSON body

        Returns:
            Parsed JSON response

        Raises:
            APIError: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        try:
            with httpx.Client() as client:
                response = client.post(url, headers=self.headers, json=json)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise APIError(f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down.")
        except httpx.ConnectError as e:
            error_msg = str(e)
            if "connection refused" in error_msg.lower():
                raise APIError("Connection refused. Check that the backend services are running.")
            elif "111" in error_msg:
                raise APIError("Connection refused (localhost:42002). Check that the services are running.")
            else:
                raise APIError(f"Connection error: {error_msg}")
        except Exception as e:
            raise APIError(f"Unexpected error: {str(e)}")

    def get_items(self) -> list:
        """Get all items (labs and tasks) from the backend.

        Returns:
            List of items
        """
        return self._get("/items/")

    def get_learners(self) -> list:
        """Get all enrolled learners.

        Returns:
            List of learners
        """
        return self._get("/learners/")

    def get_scores(self, lab: str) -> dict:
        """Get score distribution for a lab.

        Args:
            lab: Lab identifier

        Returns:
            Score distribution data
        """
        return self._get("/analytics/scores", params={"lab": lab})

    def get_pass_rates(self, lab: str) -> dict:
        """Get per-task pass rates for a lab.

        Args:
            lab: Lab identifier

        Returns:
            Pass rates data with task names and percentages
        """
        return self._get("/analytics/pass-rates", params={"lab": lab})

    def get_timeline(self, lab: str) -> dict:
        """Get submission timeline for a lab.

        Args:
            lab: Lab identifier

        Returns:
            Timeline data
        """
        return self._get("/analytics/timeline", params={"lab": lab})

    def get_groups(self, lab: str) -> dict:
        """Get per-group performance for a lab.

        Args:
            lab: Lab identifier

        Returns:
            Group performance data
        """
        return self._get("/analytics/groups", params={"lab": lab})

    def get_top_learners(self, lab: str, limit: int = 5) -> list:
        """Get top learners for a lab.

        Args:
            lab: Lab identifier
            limit: Number of top learners to return

        Returns:
            List of top learners
        """
        return self._get("/analytics/top-learners", params={"lab": lab, "limit": limit})

    def get_completion_rate(self, lab: str) -> dict:
        """Get completion rate for a lab.

        Args:
            lab: Lab identifier

        Returns:
            Completion rate data
        """
        return self._get("/analytics/completion-rate", params={"lab": lab})

    def trigger_sync(self) -> dict:
        """Trigger ETL sync to refresh data from autochecker.

        Returns:
            Sync result
        """
        return self.post("/pipeline/sync", json={})
