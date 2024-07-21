FROM --platform=linux/arm64 python:3.12 AS build

WORKDIR /all

COPY . /all

RUN pip install -r requirements.txt

ENV PYTHONPATH=/all

ENV PORT=8080

EXPOSE 8080



CMD ["python", "app/main.py"]