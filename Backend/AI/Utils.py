from langchain.schema import HumanMessage, AIMessage, SystemMessage
from Analytics.AI.Prompts import agentic_flow_prompt
from Analytics.AI.utils import extract_chat_history_as_dict, format_chat_history

def prepare_chat_memory(history_rows:list[dict],
                        user_input:str):
    messages = [SystemMessage(content=agentic_flow_prompt)]
    for msg in history_rows:
        if msg['role'].lower() == 'human':
            messages.append(HumanMessage(content=msg['message']))
        else:
            messages.append(AIMessage(content=msg['message']))
    # Append current user input as last human message
    messages.append(HumanMessage(content=user_input))

    return messages

def prepare_chat_history_for_summarization(memory:list):
    chhd = extract_chat_history_as_dict(memory)
    formatted_chat_history = format_chat_history(chhd)
    return formatted_chat_history