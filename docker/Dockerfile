FROM ubuntu:22.04

WORKDIR /app

COPY . /app

RUN  apt-get update && apt-get upgrade -y && \
     apt-get install -y python3.11 python3-dev\
                        python3-pip build-essential &&\
     pip install --upgrade pip &&\
     pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "Home.py"]