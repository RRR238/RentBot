import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class LLM:
    def __init__(self):
        self.__client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def generate_answer(self,
                 prompt,
                 model = 'gpt-3.5-turbo'
                ):

        response = self.__client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

    def get_embedding(self,
                      text_string,
                      model = 'text-embedding-3-small'):

        response = self.__client.embeddings.create(
            input=text_string,
            model=model
        )

        return response.data[0].embedding