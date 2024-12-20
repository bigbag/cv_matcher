from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel

from src.client import AIClient, ModelType


class TestResponse(BaseModel):
    name: str
    score: float


@pytest.fixture
def mock_cache_dir(tmp_path):
    return tmp_path / "cache"


@pytest.fixture
def mock_client(mock_cache_dir):
    with patch("src.client.settings") as mock_settings:
        mock_settings.cache_dir = str(mock_cache_dir)
        mock_settings.anthropic_api_key = "test_key"
        mock_settings.anthropic_model_name = "test_model"
        mock_settings.anthropic_max_tokens = 1000
        mock_settings.anthropic_temperature = 0.7
        return AIClient(ModelType.ANTHROPIC)


@pytest.mark.asyncio
async def test_run_with_string_output(mock_client):
    mock_response = MagicMock()
    mock_response.data = "test response"
    mock_response.usage = lambda: {"total_tokens": 100}

    with patch("src.client.Agent") as MockAgent:
        mock_agent = AsyncMock()
        mock_agent.run.return_value = mock_response
        MockAgent.return_value = mock_agent

        result = await mock_client.run("test prompt", use_cache=False)

        assert result == "test response"
        mock_agent.run.assert_called_once_with("test prompt")


@pytest.mark.asyncio
async def test_run_with_pydantic_output(mock_client):
    expected_response = TestResponse(name="Test", score=0.95)
    mock_response = MagicMock()
    mock_response.data = expected_response
    mock_response.usage = lambda: {"total_tokens": 100}

    with patch("src.client.Agent") as MockAgent:
        mock_agent = AsyncMock()
        mock_agent.run.return_value = mock_response
        MockAgent.return_value = mock_agent

        result = await mock_client.run("test prompt", result_type=TestResponse, use_cache=False)

        assert isinstance(result, TestResponse)
        assert result.name == "Test"
        assert result.score == 0.95


@pytest.mark.asyncio
async def test_cache_functionality(mock_client):
    test_response = "cached response"
    prompt = "test prompt"
    system_prompt = "test system prompt"

    # First call - should save to cache
    mock_response = MagicMock()
    mock_response.data = test_response
    mock_response.usage = lambda: {"total_tokens": 100}

    with patch("src.client.Agent") as MockAgent:
        mock_agent = AsyncMock()
        mock_agent.run.return_value = mock_response
        MockAgent.return_value = mock_agent

        result1 = await mock_client.run(prompt, system_prompt=system_prompt)
        assert result1 == test_response

        # Second call - should use cache
        result2 = await mock_client.run(prompt, system_prompt=system_prompt)
        assert result2 == test_response

        # Verify the agent was only called once
        assert mock_agent.run.call_count == 1


@pytest.mark.asyncio
async def test_cache_with_pydantic_model(mock_client):
    test_response = TestResponse(name="Test", score=0.95)
    prompt = "test prompt"

    mock_response = MagicMock()
    mock_response.data = test_response
    mock_response.usage = lambda: {"total_tokens": 100}

    with patch("src.client.Agent") as MockAgent:
        mock_agent = AsyncMock()
        mock_agent.run.return_value = mock_response
        MockAgent.return_value = mock_agent

        result1 = await mock_client.run(prompt, result_type=TestResponse)
        assert isinstance(result1, TestResponse)
        assert result1.name == "Test"

        result2 = await mock_client.run(prompt, result_type=TestResponse)
        assert isinstance(result2, TestResponse)
        assert result2.name == "Test"

        assert mock_agent.run.call_count == 1


def test_invalid_cache_handling(mock_client):
    cache_key = mock_client._get_cache_key("test prompt", "test system prompt")
    cache_path = mock_client._get_cache_path(cache_key)

    # Write invalid JSON to cache
    with open(cache_path, "w") as f:
        f.write("invalid json")

    result = mock_client._load_from_cache(cache_key)
    assert result is None
