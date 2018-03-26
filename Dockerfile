FROM ubuntu:16.04

RUN apt-get update \
    && apt-get install -y python3-pip supervisor \
    && apt-get clean all \
    && mkdir -p /code \
    && mkdir -p /code/tmp
ADD requirements.txt /code
ADD supervisord.conf /etc/supervisor
WORKDIR /code
RUN pip3 install --no-cache-dir -r /code/requirements.txt
EXPOSE 5000
