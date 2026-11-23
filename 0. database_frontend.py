import streamlit as st
from database_backend import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage
import uuid

st.title("Agentic AI Chatbot")

with st.chat_message('user'):
    st.text('Hi')

with st.chat_message('assistant'):
    st.text('How can I help You ?')