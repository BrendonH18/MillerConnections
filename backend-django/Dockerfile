FROM python:3.10-slim
WORKDIR /backend
ENV PYTHONUNBUFFERED = 1
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .