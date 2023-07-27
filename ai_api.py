import os
from dotenv import load_dotenv

from vectorstore import vectordb
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.schema import (
    HumanMessage,
)

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

load_dotenv()
openai_api_key = os.environ['OPENAI_API_KEY']

llm = ChatOpenAI(streaming=True,
                  callbacks=[StreamingStdOutCallbackHandler()],
                  temperature=0,
                  openai_api_key=openai_api_key)


# prompt_template = """\
# Act as an expert in Python development and use the following pieces of context 
# from the tts.readthedocs.io about Couqui TTS, a library for advanced Text-to-Speech
# generation, to answer the question step by step at the end. If you don't know the answer, 
# just say that you don't know, don't try to makeup an answer and recommend that they 
# visit https://tts.readthedocs.io/ For more information.

# {context}

# Question: {question}
# """

# PROMPT = PromptTemplate(
#     template=prompt_template, input_variables=["context", "question"]
# )


def get_query(query, collection_name):
    docsearch = vectordb_query(query, collection_name)
    response = chain_query(query, docsearch)
    return response


def vectordb_query(query, collection_name):
    db = vectordb(collection_name)
    docsearch = db.similarity_search(query)
    return docsearch


def chain_query(query, docsearch):
    chain = load_qa_chain(llm, chain_type="stuff", verbose=True,)
    return chain.run({"input_documents": docsearch, "question": query},)


if __name__ == "__main__":
    collection_name = input("Enter collection name of query: ")
    db = vectordb(collection_name)
    while True:
        query = input("What is your question? >>> ")
        docs = db.similarity_search(query=query,
                                    k=4)
        chain = load_qa_chain(llm, chain_type="stuff", verbose=True,)

        chain.run({"input_documents": docs,
                   "question": query},)
