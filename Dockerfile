FROM --platform=linux/amd64 python:3.12 AS build

WORKDIR /all

COPY . /all

RUN pip install -r requirements.txt

ENV PYTHONPATH=/all

EXPOSE ${PORT}

ENTRYPOINT ["sh", "bin/start.sh"]


