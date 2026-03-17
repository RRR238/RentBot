from Backend.Security.Security_manager import Security_manager
from langchain.chat_models import ChatOpenAI
from Shared.Vector_database.Qdrant import Vector_DB_Qdrant
from Shared.LLM import LLM

security_manager = Security_manager()
llm_langchain = ChatOpenAI(
    temperature=0.2,
    model_name="gpt-4o",
    #openai_api_key=
)

vector_db = Vector_DB_Qdrant('rent-bot-index')
llm = LLM()