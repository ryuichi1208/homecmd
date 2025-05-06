import pytest
import os
from unittest.mock import patch, call

# hello.pyからテスト対象の関数をインポート
# PYTHONPATHにカレントディレクトリが含まれている必要がある場合がある
# 例: export PYTHONPATH=$PYTHONPATH:.
from hello import check_environment_variables, log_json


@pytest.fixture(autouse=True)
def setup_env_vars(monkeypatch):
    """Ensure GEMINI_API_KEY is unset before each test unless explicitly set."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)


def test_check_environment_variables_success(monkeypatch):
    """Test check_environment_variables when GEMINI_API_KEY is set."""
    # Set the required environment variable for this test
    monkeypatch.setenv("GEMINI_API_KEY", "test_api_key_value")

    # Mock log_json to check its calls
    with patch("hello.log_json") as mock_log:
        result = check_environment_variables()

        # Assert the function returns True
        assert result is True

        # Assert that the success log message was called
        mock_log.assert_called_with("INFO", "Environment variable check passed.", status="success")


def test_check_environment_variables_failure(monkeypatch):
    """Test check_environment_variables when GEMINI_API_KEY is NOT set."""
    # Ensure the variable is unset (handled by autouse fixture, but explicit here for clarity)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    # Mock log_json to check its calls
    with patch("hello.log_json") as mock_log:
        result = check_environment_variables()

        # Assert the function returns False
        assert result is False

        # Define the expected calls to log_json
        expected_calls = [
            call(
                "ERROR",
                "Required environment variable GEMINI_API_KEY is not set",
                variable="GEMINI_API_KEY",
                description="API key for Gemini API",
            ),
            call("CRITICAL", "Missing required environment variables", missing_variables=["GEMINI_API_KEY"]),
            call("INFO", "Environment variables should be set in a .env file or as system environment variables."),
        ]

        # Assert that log_json was called with the expected arguments
        mock_log.assert_has_calls(expected_calls, any_order=False)


# --- Add more tests below ---
