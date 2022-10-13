FROM python:3

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY src src
COPY data data

CMD python3 src/main.py