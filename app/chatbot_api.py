from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from langchain_core.output_parsers import StrOutputParser

def ask(messages):
    '''
    Ask the LLM to respond to a chat message (last) given the entire chat
    Expects a sequence of messages of format ([role], [content])
        where role is human/ai/system
    '''

    prompt_template = ChatPromptTemplate.from_messages(messages)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

    chain = prompt_template | llm | StrOutputParser()
    str = chain.invoke(input={})
    return str
