import streamlit as st
from database_backend import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage
import uuid

st.title("Agentic AI Chatbot")

if 'message_history' not in st.session_state:
  st.session_state['message_history'] = []

#loading the conversation history
for message in st.session_state['message_history']:
  with st.chat_message(message['role']):
    st.text(message['content'])


#---------------------------------------------------------------------USER--------------------------------------------------------------------#
user_input = st.chat_input('Type here')

if user_input:

  #adding message to message history
  st.session_state['message_history'].append({'role': 'user', 'content' : user_input})
  
  with st.chat_message('user'):
      st.text(user_input)
  
#---------------------------------------------------------------------ASSISTANT--------------------------------------------------------------------#

  # getting response from model
  response = chatbot.invoke({'messages:' [HumanMessage(content='user_input')]})

  ai_message = response['messages'][-1].content

  #adding message to message history
  st.session_state['message_history'].append({'role': 'assistant', 'content' : ai_messages})
  
  with st.chat_message('assistant'):
      st.text(ai_messages)