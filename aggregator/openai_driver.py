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

    def rewrite_query(self, user_query: str) -> str:
        system_prompt = (
            "You are a News Search Assistant. "
            "Rewrite the user’s search query to be concise, precise, and focused on the primary topic, "
            "optimizing it for semantic similarity search in our vector database."
        )
        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query},
            ],
            temperature=0.1,
            max_tokens=50,
        )
        return response.choices[0].message.content.strip()
