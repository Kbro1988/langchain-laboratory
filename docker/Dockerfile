FROM ghcr.io/barweiss45/lc-lab-base-python:3.11-bookworm

LABEL org.opencontainers.image.source https://github.com/barweiss45/langchain-laboratory

# NEED TO RUN HEALTHCHECK
RUN  apt-get update &&\
     apt-get install dnsutils -y

RUN  pip install --upgrade pip &&\
     pip install -r requirements.txt
     
WORKDIR /app

COPY . /app

EXPOSE 8501

# Will use 'localhost' by default if not defined in the docker-compose.yml
ARG FQDN=localhost

ENV FQDN=${FQDN}

HEALTHCHECK --interval=1m --timeout=10s \
  CMD /bin/bash docker/healthcheck.sh $FQDN || exit 1

CMD ["streamlit", "run", "Home.py"]