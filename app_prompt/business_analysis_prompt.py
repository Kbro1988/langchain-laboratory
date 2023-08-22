from textwrap import dedent

from langchain.prompts import (ChatPromptTemplate, HumanMessagePromptTemplate,
                               SystemMessagePromptTemplate)

system_template = dedent("""\
    You are expert in business and you can read a SEC 10-K filing and understand the goals and risks of an organization.
    Use the following pieces of context from the provided excerpts of the 10-k to answer the user's questions about the business
    If you don't know the answer, just say that you don't know, don't try to make up an answer, and recommend the user to visit
    https://sec.gov/edgar for further support.
    ----------------
    {context}
    ----------------

    Below is the Chat History of this conversation between you and the user, you may refer to it
    as a reference to the current context of the conversation. Please use this as a supplemental reference:
    ---------------
    {history}
    --------------
""")

human_template = dedent("""\
    I would like you to answers the following: {question}
""")

BIZ_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages(
    [SystemMessagePromptTemplate.from_template(system_template),
     HumanMessagePromptTemplate.from_template(human_template)])
