from textwrap import dedent

from langchain.prompts import (ChatPromptTemplate, HumanMessagePromptTemplate,
                               SystemMessagePromptTemplate)

system_template = dedent("""\
    You are an excellent AI assistant that is able to review multiple excerpts
    of content below and make informed responses to the human based on this context.
    Use following pieces of context below. Furthermore you may, ask follow up questions
    if you need more infomation for the human. You can use the Chat history to help you
    understand the context too. If you don't know the answer, just say that you don't
    know, don't try to make up an answer or ask a question to help you understand the
    request.
    ----------------
    {context}
    ----------------

    Here is the Chat History. Please use this as a coreference:
    ---------------
    {history}
    --------------
""")

human_template = dedent("""\
    I would like to know: {question}
""")

COMBINE_DOC_PROMPT = ChatPromptTemplate.from_messages(
    [SystemMessagePromptTemplate.from_template(system_template),
     HumanMessagePromptTemplate.from_template(human_template)])
