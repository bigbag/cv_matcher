import hashlib
import json
from pathlib import Path
from typing import Optional, Type, Union

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.settings import ModelSettings

from src.conf import settings
from src.entities import ModelConfig, ModelType
from src.interfaces import AIClientInterface
from src.logger import create_logger

logger = create_logger(__name__)

DEFAULT_SYSTEM_PROMPT = """
    You are a job matcher. 
    You are given a resume and a job description. 
    You are to match the resume to the job description.
"""


MODEL_CONFIGS = {
    ModelType.ANTHROPIC: ModelConfig(
        model_name=settings.anthropic_model_name,
        api_key=settings.anthropic_api_key,
        max_tokens=settings.anthropic_max_tokens,
        temperature=settings.anthropic_temperature,
    ),
    ModelType.OPENAI: ModelConfig(
        model_name=settings.openai_model_name,
        api_key=settings.openai_api_key,
        max_tokens=settings.openai_max_tokens,
        temperature=settings.openai_temperature,
    ),
}

MODEL_CLASSES = {
    ModelType.ANTHROPIC: AnthropicModel,
    ModelType.OPENAI: OpenAIModel,
}


class AIClient(AIClientInterface):
    def __init__(self, model_type: ModelType, max_tokens: Optional[int] = None):
        config = MODEL_CONFIGS[model_type]
        model_class = MODEL_CLASSES[model_type]

        self._model = model_class(config.model_name, api_key=config.api_key)
        self._model_settings = ModelSettings(
            max_tokens=max_tokens or config.max_tokens,
            temperature=config.temperature,
        )
        self._cache_dir = Path(settings.cache_dir)
        self._cache_dir.mkdir(exist_ok=True)

    def _get_cache_key(self, prompt: str, system_prompt: str) -> str:
        """Generate a cache key from the prompt and system prompt."""
        content = f"{prompt}|{system_prompt}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the full path for a cache file."""
        return self._cache_dir / f"{cache_key}.json"

    def _save_to_cache(self, cache_key: str, result: Union[str, BaseModel]) -> None:
        """Save the result to cache."""
        cache_path = self._get_cache_path(cache_key)
        data = result if isinstance(result, str) else result.model_dump()
        with open(cache_path, "w") as f:
            json.dump({"data": data, "type": type(result).__name__}, f)

    def _load_from_cache(
        self, cache_key: str, result_type: Optional[Type[BaseModel]] = None
    ) -> Optional[Union[str, BaseModel]]:
        """Load the result from cache if it exists."""
        cache_path = self._get_cache_path(cache_key)
        if not cache_path.exists():
            return None

        try:
            with open(cache_path) as f:
                cached = json.load(f)
                if cached["type"] == "str":
                    return cached["data"]
                elif result_type and cached["type"] == result_type.__name__:
                    return result_type.model_validate(cached["data"])
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            return None

    async def run(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        result_type: Optional[Type[BaseModel]] = None,
        use_cache: bool = True,
    ) -> Union[str, BaseModel]:
        """
        Run the AI model with the given prompt and parameters.

        Args:
            prompt: The input prompt for the model
            max_tokens: Optional override for max tokens
            system_prompt: System prompt to use (defaults to job matcher prompt)
            result_type: Optional Pydantic model to structure the output
        """
        cache_key = self._get_cache_key(prompt, system_prompt)
        cached_result = self._load_from_cache(cache_key, result_type)
        if use_cache and cached_result is not None:
            logger.debug("Using cached response")
            return cached_result

        model_settings = self._model_settings.copy()
        if max_tokens is not None:
            model_settings["max_tokens"] = max_tokens

        agent = Agent(
            model=self._model,
            model_settings=model_settings,
            system_prompt=system_prompt,
        )
        if result_type:
            agent = Agent(
                model=self._model,
                model_settings=model_settings,
                system_prompt=system_prompt,
                result_type=result_type,
            )

        result = await agent.run(prompt)
        logger.debug(f"Request usage: {result.usage()}")

        if use_cache:
            self._save_to_cache(cache_key, result.data)
        return result.data
