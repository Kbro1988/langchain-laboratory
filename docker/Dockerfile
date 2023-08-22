FROM python:3.11-bookworm

WORKDIR /app

COPY . /app

RUN  pip install --upgrade pip &&\
     pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "Home.py"]