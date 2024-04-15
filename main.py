#pip install streamlit langchain langchain-openai beautifulsoup4 chomadb
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

load_dotenv()



def get_vectorstore_from_url(url):

    # get the text in document form
    loader = WebBaseLoader(url)
    document = loader.load()

    # split the document into chunks
    text_splitter = RecursiveCharacterTextSplitter()
    document_chunks = text_splitter.split_documents(document)

    # Create vector store from chunks
    vector_store = Chroma.from_documents(document_chunks, OpenAIEmbeddings())

    return vector_store
    
    return document_chunks

def get_context_retriever_chain(vector_store):
    llm = ChatOpenAI()

    retriever = vector_store.as_retriever()

    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        ("user", "generate a search query to look up in order to get information relevant to the conversation")
    ])
    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)

    return retriever_chain

def get_conversational_rag_chain(retriever_chain):

    llm = ChatOpenAI()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer the user's questions based on the below context:\n\n{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}")
    ])
    

    stuff_documents_chain = create_stuff_documents_chain(llm, prompt)

    return create_retrieval_chain(retriever_chain, stuff_documents_chain)

def get_response(user_input):
    retriever_chain = get_context_retriever_chain(st.session_state.vectore_store)
    conversation_rag_chain =  get_conversational_rag_chain(retriever_chain)

         # response = get_response(user_query)
    response = conversation_rag_chain.invoke({
            "chat_history": st.session_state.chat_history,
            "input": user_query
        })
    return response["answer"]

# App Config
st.set_page_config(page_title="Flexdevs Chatbot", page_icon="robot head")
st.title("Chat with websites")


# Sidebar
with st.sidebar:
    st.header("Settings")
    website_url = st.text_input("Website URL")

if website_url is None or website_url =="":
    st.info("Please enter a website URL in Settings to proceed")

else:

    # make the history of chat persist otherwise print AIMessage to sidebar
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(content="Hello, I'm Flexdev, how can I help you with this website")    
    ]
    if "vector_store" not in st.session_state:
        st.session_state.vectore_store = get_vectorstore_from_url(website_url)


    # Create conversation state    
    vector_store = get_vectorstore_from_url(website_url)
    retriever_chain = get_context_retriever_chain(vector_store)
    # document_chunks = get_vectorstore_from_url(website_url)
    # Debug will display output on sidebar
    # with st.sidebar:
    #     st.write(document_chunks)

    # User input
    user_query = st.chat_input("Type your message here...")
    if user_query is not None and user_query !="":
   
        response = get_response(user_query)
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        st.session_state.chat_history.append(AIMessage(content=response))

        # retrieved_documents = retriever_chain.invoke({
        #     "chat_history": st.session_state.chat_history,
        #     "input": user_query
        # })
        # st.write(retrieved_documents)
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

    








    