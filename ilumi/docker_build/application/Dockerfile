FROM python:3.5

RUN apt-get -y update

# Install Python.
RUN apt-get -y install python
RUN pip3 install --upgrade pip
RUN pip3 install -U nltk

ENV APP_DIR=/usr/src/app
# ENV APP_DIR=/home/app/

# ENV CORPORA all
# CMD python -m nltk.downloader $CORPORA; python

WORKDIR ${APP_DIR}

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ADD . .
EXPOSE 5000
CMD python run.py --logging=debug
