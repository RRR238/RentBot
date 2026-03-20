import os
from typing import Optional
from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI

load_dotenv()


class LLM:
    def __init__(self, client: OpenAI = None):
        self.__client = client or OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def generate_answer(
        self,
        prompt: str,
        model: str = 'gpt-3.5-turbo',
        temperature: float = 0.0,
        system_prompt: Optional[str] = None,
        chat_history: Optional[list[dict]] = None,
    ) -> str:
        messages = self._build_messages(prompt, system_prompt, chat_history)
        response = self.__client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=messages,
        )
        return response.choices[0].message.content

    @staticmethod
    async def generate_answer_static_async(
        async_client: AsyncOpenAI,
        prompt: str,
        model: str = 'gpt-3.5-turbo',
        temperature: float = 0.0,
        system_prompt: Optional[str] = None,
        chat_history: Optional[list[dict]] = None,
    ) -> str:
        messages = LLM._build_messages(prompt, system_prompt, chat_history)
        response = await async_client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=messages,
        )
        return response.choices[0].message.content

    def get_embedding(self, text_string: str, model: str = 'text-embedding-3-small') -> list:
        response = self.__client.embeddings.create(input=text_string, model=model)
        return response.data[0].embedding

    @staticmethod
    async def get_embedding_static_async(
        async_client: AsyncOpenAI,
        text_string: str,
        model: str = 'text-embedding-3-small',
    ) -> list:
        response = await async_client.embeddings.create(input=text_string, model=model)
        return response.data[0].embedding

    @staticmethod
    def _build_messages(
        prompt: Optional[str],
        system_prompt: Optional[str],
        chat_history: Optional[list[dict]],
    ) -> list[dict]:
        messages = []
        if system_prompt:
            messages.append({"role": "system",
                             "content": system_prompt})
        if chat_history:
            messages.extend(chat_history)
        if prompt:
            messages.append({"role": "user",
                             "content": prompt})
        return messages
