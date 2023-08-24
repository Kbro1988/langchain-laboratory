FROM ghcr.io/barweiss45/lc-lab-base-python:3.11-bookworm

LABEL org.opencontainers.image.source https://github.com/barweiss45/langchain-laboratory

RUN  pip install --upgrade pip &&\
     pip install -r requirements.txt
     
WORKDIR /app

COPY . /app

EXPOSE 8501

CMD ["streamlit", "run", "Home.py"]