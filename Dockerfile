FROM python:3.11

WORKDIR /usr/app

RUN apt-get update --fix-missing && apt-get upgrade -y

ENV PYTHONUNBUFFERED=1

RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools

ADD requirements.txt .
RUN pip3 install -r requirements.txt

ADD ./ ./

EXPOSE 8000

CMD [ "python3", "-u", "./main.py" ]