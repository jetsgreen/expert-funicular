import streamlit as st
# Storing the converstion between AI and Human, we need to use the schemas provided by langchain: see imports below
from langchain_core.messages import AIMessage, HumanMessage

def get_response(user_input):
    return "I don't know"

# App Config
st.set_page_config(page_title="Flexdevs Chatbot", page_icon="robot head")
st.title("Chat with websites")

# make the history of chat persist otherwise print AIMessage to sidebar
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
    AIMessage(content="Hello, I'm Flexdev and I'm a chatbot, how can I help you")    
    ]

# Sidebar
with st.sidebar:
    st.header("Settings")
    website_url = st.text_input("Website URL")

# User input
user_query = st.chat_input("Type your message here...")
if user_query is not None and user_query !="":
    response = get_response(user_query)
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    st.session_state.chat_history.append(AIMessage(content=response))
    # Now that we added the code to collect chat history, we won't need the test code below
    # with st.chat_message("Human"):
    #      st.write(user_query)
    # with st.chat_message("AI"):
    #     st.write(response)

# For debugging, let's log the chat history to sidebar
# with st.sidebar:
#     st.write(st.session_state.chat_history)
# Any time an event happens in Streamlit, the whole DOM refreshes

# Converstion
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)





    