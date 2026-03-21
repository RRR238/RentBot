from Backend.Security.Security_manager import Security_manager
from Shared.Vector_database.Qdrant import Vector_DB_Qdrant
from Shared.LLM import LLM

security_manager = Security_manager()
vector_db = Vector_DB_Qdrant('rent-bot-index')
llm = LLM()