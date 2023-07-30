from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    )
from textwrap import dedent

system_template = dedent("""\
    Act as an expert in Git and GitOps that can help new users of Git and
    version control learn about Git. Use following pieces of context from the
    2nd Edition of Pro Git by Scott Chacon and Ben Straub to answer the users
    question. If you don't know the answer, just say that you don't know, don't
    try to make up an answer and suggest that the user visit https://git-scm.com/
    for further support.
    ----------------
    {context}
    ----------------
""")

human_template = dedent("""\
    I would like to know: {question}
""")

GIT_BOOK_PROMPT = ChatPromptTemplate.from_messages(
    [SystemMessagePromptTemplate.from_template(system_template),
     HumanMessagePromptTemplate.from_template(human_template)])
