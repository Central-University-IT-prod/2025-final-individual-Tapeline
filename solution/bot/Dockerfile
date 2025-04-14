FROM python:3.13.2-alpine3.21

WORKDIR /app
COPY . .
RUN chmod +x ./start.sh

RUN pip3 install poetry
RUN poetry install

CMD chmod +x ./start.sh ; ./start.sh
