import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class LLM:
    def __init__(self):
        self.__client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def generate_answer(self,
                        prompt,
                        model='gpt-3.5-turbo',
                        temperature=0.0,  # <-- default temperature here
                        chat_history=None  # Allow chat_history to be passed or initialized
                        ):
        # If no chat history is passed, create a default empty list
        if chat_history is None:
            chat_history = []

        # Add the user prompt to the chat history
        user_message = {"role": "user", "content": prompt}
        chat_history.append(user_message)

        # Call OpenAI API with the accumulated chat history
        response = self.__client.chat.completions.create(
            model=model,
            temperature=temperature,  # <-- passed into the API call
            messages=chat_history  # <-- the chat history (including the new user prompt)
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
