FROM python:3.12.1-alpine3.19

WORKDIR /app

RUN apk add curl

COPY . .
RUN chmod +x ./start.sh

RUN pip3 install poetry
RUN poetry install --without dev

CMD chmod +x ./start.sh ; ./start.sh
