FROM ubuntu:latest

RUN apt-get -y update; \
    apt-get -y upgrade; \
    apt-get -y install apt-utils 
COPY ./seawords /app/seawords
WORKDIR /app

CMD ["bash"]
