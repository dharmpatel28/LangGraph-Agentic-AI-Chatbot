import streamlit as st
from database_backendwithLangsmith import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage
import uuid

st.title("Agentic AI Chatbot")


#--------------------------------------------------------------utility function------------------------------------------------------------------------

def generate_thread_id():
  thread_id = uuid.uuid4()
  return str(thread_id)

def reset_chat():
  thread_id = generate_thread_id()
  st.session_state['thread_id'] = thread_id
  add_thread(st.session_state['thread_id'])
  st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
      st.session_state['chat_threads'].append(thread_id)

    if thread_id not in st.session_state['thread_titles']:
      st.session_state['thread_titles'][thread_id] = "New Chat"

def load_conversation(thread_id):
  return chatbot.get_state(config={'configurable': {'thread_id' : str(thread_id)}}).values['messages']

#loads titles from existing conversations
def load_thread_title(thread_id):
  messages = load_conversation(thread_id)
  for msg in messages:
    if isinstance(msg, HumanMessage):
      title = str(msg.content).strip()
      return title
  return "New Chat"

#--------------------------------------------------------------session setup------------------------------------------------------------------------

if 'message_history' not in st.session_state:
  st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
  st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
  st.session_state['chat_threads'] = retrieve_all_threads()

if 'thread_titles' not in st.session_state:
    st.session_state['thread_titles'] = {}

    for thread_id in st.session_state['chat_threads']:
        st.session_state['thread_titles'][thread_id] = (
            load_thread_title(thread_id)
        )

add_thread(st.session_state['thread_id'])

#--------------------------------------------------------------Sidebar UI------------------------------------------------------------------------
st.sidebar.title('LangGraph ChatBot')

if st.sidebar.button('New Chat'):
  reset_chat()

st.sidebar.header('My Conversation')

for thread_id in st.session_state['chat_threads']:

  title = st.session_state['thread_titles'].get(thread_id, "New Chat")

  if title == "New Chat":
        continue

  if st.sidebar.button(title, key=str(thread_id)):

    st.session_state['thread_id'] = thread_id

    messages = load_conversation(thread_id)

    temp_messages = []

    for msg in messages:

      if isinstance(msg, HumanMessage):
        role = 'user'
      
      else:
        role = 'assistant'

      temp_messages.append({'role':role, 'content': msg.content})
  
    st.session_state['message_history'] = temp_messages

    # st.rerun()


#--------------------------------------------------------------Main UI------------------------------------------------------------------------

CONFIG = {'configurable': {'thread_id' :  st.session_state['thread_id']},
          "metadata":{"thread_id": st.session_state["thread_id"]}, 
          "run_name": "chat_turn",}

#loading the conversation history
for message in st.session_state['message_history']:
  with st.chat_message(message['role']):
    st.text(message['content'])


#---------------------------------------------------------------------USER--------------------------------------------------------------------#
user_input = st.chat_input('Type here')

if user_input:

  thread_id = st.session_state['thread_id']

  if st.session_state['thread_titles'][thread_id] == "New Chat":
    st.session_state['thread_titles'][thread_id] = user_input[:35]

  #adding message to message history
  st.session_state['message_history'].append({'role': 'user', 'content' : user_input})
  
  with st.chat_message('user'):
      st.text(user_input)
  
#---------------------------------------------------------------------ASSISTANT--------------------------------------------------------------------#

  with st.chat_message('assistant'):
      ai_message = st.write_stream(
        message_chunk.content for message_chunk, metadata in chatbot.stream(
          {'messages': [HumanMessage(content=user_input)]}, 
          config=CONFIG,
          stream_mode = 'messages'
        )
      )

  st.session_state['message_history'].append({'role': 'assistant', 'content' : ai_message})

  #--------------------Move recently active conversations to the top---------------------------------------------

  thread_id = st.session_state['thread_id']

  if thread_id in st.session_state['chat_threads']:
      st.session_state['chat_threads'].remove(thread_id)

  st.session_state['chat_threads'].insert(0, thread_id)

  #-------------------------------------------------------------------------------------------------------------------

  st.rerun()




