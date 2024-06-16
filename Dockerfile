FROM python:3.9.13

WORKDIR /app
COPY . /app

EXPOSE 5000

RUN pip3 install -r requirements.txt
RUN python3 run.py