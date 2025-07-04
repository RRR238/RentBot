from langchain.chat_models import ChatOpenAI
from Shared.Vector_database.Qdrant import Vector_DB_Qdrant

gen_model = "gpt-4o"

llm_langchain = ChatOpenAI(
    temperature=0.2,
    model_name="gpt-4o",
    #openai_api_key=
)

vdb = Vector_DB_Qdrant('rent-bot-index')