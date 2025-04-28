from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from Prompts import get_key_attributes_prompt, agentic_flow_prompt, check_conversation_prompt,summarize_chat_history_prompt
from utils import convert_text_to_dict, processing_dict, prepare_filters, extract_chat_history_as_dict, format_chat_history
from Shared.Elasticsearch import Vector_DB
from Shared.LLM import LLM
from Shots import chat_history_summary_few_shots
import warnings
from langchain.schema import SystemMessage

warnings.filterwarnings("ignore",
                        category=DeprecationWarning)
warnings.filterwarnings("ignore",
                        category=UserWarning)


llm_langchain = ChatOpenAI(
    temperature=0.2,
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

org_summary = ""
while True:
    query = input()
    chhd = extract_chat_history_as_dict(memory)
    formated_chat_history = format_chat_history(chhd)
    # response_query_classification = llm.generate_answer(check_conversation_prompt.format(user_prompt=query,
    #                                                                                      chat_history=formated_chat_history))
    # print(response_query_classification)
    response = agentic_chain.predict(input = query)
    response_summary = llm.generate_answer(summarize_chat_history_prompt.format(original_summary=org_summary,
                                                                                user_prompt=query),
                                                                    chat_history=chat_history_summary_few_shots)
    org_summary = response_summary
    print(f"🤖: {response}")
    print(f"summary: {response_summary}")
