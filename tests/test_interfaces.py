import pytest
from pydantic import BaseModel

from src.entities import ModelType
from src.interfaces import AIClientInterface


class TestResponse(BaseModel):
    message: str


class MockAIClient(AIClientInterface):
    async def run(
        self,
        prompt: str,
        max_tokens: None = None,
        system_prompt: str = "",
        result_type: None = None,
    ) -> str:
        return "mock response"


class TypedMockAIClient(AIClientInterface):
    async def run(
        self,
        prompt: str,
        max_tokens: None = None,
        system_prompt: str = "",
        result_type: None = None,
    ) -> TestResponse:
        return TestResponse(message="mock response")


def test_ai_client_interface_initialization():
    client = MockAIClient(model_type=ModelType.OPENAI, max_tokens=100)
    assert isinstance(client, AIClientInterface)


@pytest.mark.asyncio
async def test_mock_client_run():
    client = MockAIClient(model_type=ModelType.OPENAI)
    response = await client.run("test prompt")
    assert isinstance(response, str)
    assert response == "mock response"


@pytest.mark.asyncio
async def test_typed_mock_client_run():
    client = TypedMockAIClient(model_type=ModelType.OPENAI)
    response = await client.run("test prompt", result_type=TestResponse)
    assert isinstance(response, TestResponse)
    assert response.message == "mock response"


@pytest.mark.asyncio
async def test_client_with_system_prompt():
    client = MockAIClient(model_type=ModelType.ANTHROPIC)
    response = await client.run(prompt="test prompt", system_prompt="You are a helpful assistant")
    assert isinstance(response, str)


@pytest.mark.asyncio
async def test_client_with_max_tokens():
    client = MockAIClient(model_type=ModelType.OPENAI, max_tokens=50)
    response = await client.run(prompt="test prompt", max_tokens=100)  # Override instance max_tokens
    assert isinstance(response, str)
