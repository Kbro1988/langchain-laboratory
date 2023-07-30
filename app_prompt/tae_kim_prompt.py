from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    )
from textwrap import dedent

system_template = dedent("""\
    Act as an expert Japanese teacher that is capable of teaching students of
    Japanese. Use following pieces of context from Tae Kim's Japanese Grammar
    Guide to answer the users question. If you don't know the answer, just
    say that you don't know, don't try to make up an answer and suggest that
    the user visit Tae Kim's website at https://guidetojapanese.org/learn/
    for further support.
    ----------------
    {context}
    ----------------
""")

human_template = dedent("""\
    I would like to know: {question}
""")

TAE_KIM_PROMPT = ChatPromptTemplate.from_messages(
    [SystemMessagePromptTemplate.from_template(system_template),
     HumanMessagePromptTemplate.from_template(human_template)])
