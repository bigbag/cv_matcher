from typing import Optional, Type, Union

from pydantic import BaseModel

from src.entities import ModelType


class AIClientInterface:
    def __init__(self, model_type: ModelType, max_tokens: Optional[int] = None):
        pass

    async def run(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        system_prompt: str = "",
        result_type: Optional[Type[BaseModel]] = None,
    ) -> Union[str, BaseModel]:
        pass
