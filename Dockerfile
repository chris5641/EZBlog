FROM ubuntu:16.04

RUN apt-get update \
    && apt-get install -y python3-pip supervisor \
    && apt-get clean all \
    && mkdir -p /code
ADD requirements.txt /code
ADD supervisord.conf /etc/supervisor
WORKDIR /code
RUN pip3 install --no-cache-dir -r /code/requirements.txt \
    && mkdir -p /code/tmp
EXPOSE 5000
