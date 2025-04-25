from types import ModuleType

from loguru import logger
from openai import OpenAI, OpenAIError


class OpenaiDriver:
    def __init__(self, config: ModuleType):
        self.config = config
        self.client = OpenAI(api_key=self.config.OPENAI_API_KEY)

    async def get_embedding(self, text: str) -> list[float] | None:
        logger.debug(f"Requesting embedding in {self}")
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.config.EMBEDDING_MODEL,
                dimensions=self.config.VECTOR_DIMENSION,
            )
        except OpenAIError as exp:
            logger.exception(exp)
            return None
        return response.data[0].embedding
