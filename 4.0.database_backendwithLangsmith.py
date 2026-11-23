from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFacePipeline
from transformers import pipeline
import sqlite3

from langchain_openai import ChatOpenAI


load_dotenv( "/content/drive/MyDrive/Colab Notebooks/Langraph_AgenticAI/.env", override=True )

# pipe = pipeline(
#     "text-generation",
#     model="HuggingFaceTB/SmolLM2-135M-Instruct",
#     device_map="auto",
#     max_new_tokens=256,
#     return_full_text=False
# )

# llm = HuggingFacePipeline(pipeline=pipe)

from langchain_groq import ChatGroq

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    streaming=True
)

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
# Checkpointer
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)



# def retrieve_all_threads():

#     all_threads = []
#     seen_threads = set()

#     for checkpoint in checkpointer.list(None):

#         thread_id = checkpoint.config['configurable']['thread_id']

#         if thread_id not in seen_threads:
#             seen_threads.add(thread_id)
#             all_threads.append(thread_id)

#     return all_threads


def retrieve_all_threads():

    latest_checkpoints = {}

    for checkpoint in checkpointer.list(None):

        thread_id = str( checkpoint.config['configurable']['thread_id'] )

        checkpoint_id = checkpoint.config['configurable'].get( 'checkpoint_id', '' )

        # Keep the latest checkpoint for each thread
        if (
            thread_id not in latest_checkpoints
            or checkpoint_id > latest_checkpoints[thread_id]
        ):
            latest_checkpoints[thread_id] = checkpoint_id

    # Sort threads from newest activity to oldest
    sorted_threads = sorted(
        latest_checkpoints,
        key=lambda thread_id: latest_checkpoints[thread_id],
        reverse=True
    )

    return sorted_threads
