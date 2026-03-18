import os
from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI

load_dotenv()


class LLM:
    def __init__(self, client: OpenAI = None):
        self.__client = client or OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.__async_client = AsyncOpenAI(api_key=self.__client.api_key)

    def generate_answer(self, prompt: str, model: str = 'gpt-3.5-turbo', temperature: float = 0.0) -> str:
        response = self.__client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    async def generate_answer_async(self, prompt: str, model: str = 'gpt-3.5-turbo', temperature: float = 0.0) -> str:
        response = await self.__async_client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def get_embedding(self, text_string: str, model: str = 'text-embedding-3-small') -> list:
        response = self.__client.embeddings.create(input=text_string, model=model)
        return response.data[0].embedding

    async def get_embedding_async(self, text_string: str, model: str = 'text-embedding-3-small') -> list:
        response = await self.__async_client.embeddings.create(input=text_string, model=model)
        return response.data[0].embedding
