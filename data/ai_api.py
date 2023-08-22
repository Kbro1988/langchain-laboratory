#! /usr/bin/env python3

import argparse
from textwrap import dedent

import langchain
#from langchain.cache import InMemoryCache
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import RetrievalQA
from langchain.chains.question_answering import load_qa_chain
from langchain.chains.question_answering.stuff_prompt import \
    CHAT_PROMPT as LG_PROMPT
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationStringBufferMemory

from app_prompt import (BIZ_ANALYSIS_PROMPT, COMBINE_DOC_PROMPT,
                        GIT_BOOK_PROMPT, TAE_KIM_PROMPT)
from data.chroma_db import chroma_vectordb
from config import Config
from data.weaviate_db import weaviate_vectordb

# Load config settings
configs = Config()

logger = configs.logger

# Retrieve OpenAI API Key from .env file
openai_api_key = configs.OPENAI_API_KEY

# When using Chat_Models the llm_cache will improve performance
# langchain.llm_cache = InMemoryCache() # Turn this off when you want to test various models
langchain.debug = True

memory = ConversationStringBufferMemory(input_key="question", return_messages=True,)


AVAILABLE_PROMPTS = ["LG_PROMPT - Gen Use",
                     "TK_CHAT_PROMPT",
                     "GIT_BOOK_PROMPT",
                     "COMBINE_DOC_PROMPT",
                     "BIZ_ANALYSIS_PROMPT", ]

MODELS = ["gpt-3.5-turbo",
          "gpt-3.5-turbo-0613",
          "gpt-3.5-turbo-16k-0613",
          "gpt-4-0613",
          ]


def get_query(model, query, vectordb_choice, collection_name, text_key="text", prompt="LG_PROMPT", 
              chain_type="stuff", search_name="Similarity", k_value=4, **kwargs) -> list[str]:

    logger.info("Query Values: %s | %s | %s | %s | %s | %d", query, vectordb_choice, collection_name, prompt, search_name, k_value)
    llm = ChatOpenAI(streaming=True, callbacks=[StreamingStdOutCallbackHandler()], temperature=0, openai_api_key=openai_api_key, model=model,)

    # Set the Vectore Store Based on vectordb_choice
    if vectordb_choice == "ChromaDB":
        db = chroma_vectordb(collection_name)
    elif vectordb_choice == "Weaviate":
        db = weaviate_vectordb(collection_name, text_key)
    else:
        raise ValueError("'collection_name' must defined.")

    search_kwargs = {"k": k_value}
    if kwargs:
        search_kwargs.update(**kwargs)

    search_dict = {
        "Similarity": "similarity",
        "MMR": "mmr",
        "Similarity and Display Score": "Score",
        "Similarity with Score Threshold": "similarity_score_threshold",
        "Filter": None
    }

    search_type = search_dict[search_name]

    if search_type == "Score":
        docsearch = db.similarity_search_with_score(query)
        docsearch_no_tup = [doc[0] for doc in docsearch]  # Remove Score from tuple
        response = chain_query(llm, query, docsearch_no_tup, prompt)  # Can not use the score object.
        return [response, docsearch]
    elif search_type is not None:
        retriever = db.as_retriever(search_type=search_type, search_kwargs=search_kwargs)
    else:
        # For Filter based retriever
        retriever = db.as_retriever(search_kwargs={"filter": search_kwargs})
    response = retrieval_qa(llm, query, prompt, retriever=retriever, chain_type=chain_type, return_source_documents=True)
    return response


def vectordb_search_with_score(vectordb_choice, query, collection_name, text_key, k_value) -> tuple:
    if vectordb_choice == "ChromaDB":
        db = chroma_vectordb(collection_name)
        docsearch = db.similarity_search_with_score(query)
        return docsearch
    elif vectordb_choice == "Weaviate":
        db = weaviate_vectordb(collection_name, text_key)
        docsearch = db.similarity_search_with_score(query, k_value, by_text=False)
        return docsearch


def prompt_selector(prompt):
    prompts = {"LG_PROMPT - Gen Use": LG_PROMPT,
               "TK_CHAT_PROMPT": TAE_KIM_PROMPT,
               "GIT_BOOK_PROMPT": GIT_BOOK_PROMPT,
               "COMBINE_DOC_PROMPT": COMBINE_DOC_PROMPT,
               "BIZ_ANALYSIS_PROMPT": BIZ_ANALYSIS_PROMPT,
               }
    if prompt not in prompts:
        raise ValueError(f"Invalid Prompt Name: {prompt}.")
    return prompts[prompt]


def chain_query(llm, query, docsearch, prompt):
    # Initialize Memory Buffer for Conversation
    prompt_template = prompt_selector(prompt)
    chain = load_qa_chain(llm, chain_type="stuff",
                          verbose=True,
                          prompt=prompt_template,
                          memory=memory)
    return chain.run({"input_documents": docsearch, "question": query},)

def retrieval_qa(llm: ChatOpenAI, query: str, prompt: str, retriever, chain_type: str ="stuff", return_source_documents: bool =False)-> dict[str]:
    # Initialize Memory Buffer for Conversation
    if chain_type in ["map_reduce", "refine", "map_rerank"]:
        qa_chain = load_qa_chain(llm, chain_type=chain_type,)
    else:
        prompt_template = prompt_selector(prompt)
        qa_chain = load_qa_chain(llm, chain_type=chain_type, prompt=prompt_template, memory=memory)
    qa = RetrievalQA(combine_documents_chain=qa_chain, retriever=retriever, verbose=True, return_source_documents=return_source_documents)
    return qa(query)


def load_memory():
    # Simple function to return history buffer
    output = memory.load_memory_variables({''})
    return output


def clear_memory():
    # Simple Function to reset Chat memory
    memory.clear()


def main(args):
    # if args.log_level:
    #     configure_logging(level=args.log_level)
    if args.collection:
        collection_name = args.collection
    else:
        collection_name = input("Enter collection name of query: ")
    if args.prompt:
        prompt = args.prompt
    else:
        prompt = "LG_PROMPT - Gen Use"
    db = chroma_vectordb(collection_name)
    while True:
        query = input("What is your question? >>> ")
        docsearch = db.similarity_search(query=query, k=4)
        chain_query(llm=ChatOpenAI(streaming=True,
                                   callbacks=[StreamingStdOutCallbackHandler()],
                                   temperature=0,
                                   openai_api_key=openai_api_key),
                    query=query,
                    docsearch=docsearch,
                    prompt=prompt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description="ai_api.py - The module that deals with the AI logic for this application",
                                     epilog=dedent("""
                                            Usage examples:
                                            1. Run with default log level and prompt:

                                            `python your_script.py -c your_collection_name`

                                            2. Set log level to 'info' and use TK_CHAT_PROMPT:

                                            `python your_script.py -l info -c your_collection_name -p TK_CHAT_PROMPT`

                                            Please note:
                                            - NOT IN SERVICE! The --log-level argument is optional. If not provided, the script will use the default log level.
                                            - The --collection argument is optional and you can enter it when the program starts too. The Vector Store
                                              collection must already be created.
                                            - The prompt can be selected using the -p or --prompt argument. If not used, LG_PROMPT - Gen Use is the default.
                                            - Make sure to set the OPENAI_API_KEY environment variable with your valid OpenAI API key before running the script.
                                            """))

    # parser.add_argument("-l", "--log-level", type=str, help="Set the logging level of func_logger.")
    parser.add_argument("-c", "--collection", type=str, help="Set the Vector DB Collection to be queried.")
    parser.add_argument("-p", "--prompt", type=str, help="Set the prompt template. Default is LG_PROMPT.")
    args = parser.parse_args()
    main(args)
