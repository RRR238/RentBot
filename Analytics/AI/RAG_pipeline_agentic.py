from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from Prompts import get_key_attributes_prompt, agentic_flow_prompt
from utils import convert_text_to_dict, processing_dict, prepare_filters
from Shared.Elasticsearch import Vector_DB
from Shared.LLM import LLM
from Shots import agentic_flow_few_shots
import warnings
from langchain.schema import SystemMessage

llm_langchain = ChatOpenAI(
    temperature=0,
    model_name="gpt-3.5-turbo",
    #openai_api_key=,  # optional if set as ENV variable
)
llm = LLM()
vdb = Vector_DB('rent-bot-index')

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)
system_instruction = SystemMessage(
    content=agentic_flow_prompt
)

memory.chat_memory.messages.append(system_instruction)

agentic_prompt = ChatPromptTemplate.from_messages([
    system_instruction,
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

agentic_chain = LLMChain(
    llm=llm_langchain,
    prompt=agentic_prompt,
    memory=memory
)

while True:
    query = input()
    response = agentic_chain.predict(input = query)
    print(response)