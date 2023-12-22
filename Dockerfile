FROM python:3.11-alpine

RUN pip install --upgrade pip

RUN pip3 install poetry
#RUN poetry config virtualenvs.create false

RUN mkdir /app
WORKDIR /app

COPY pyproject.toml /app
COPY src /app

#RUN pip3 install bot_assistant_mx-0.0.1-py3-none-any.whl

RUN poetry install

CMD ["poetry", "run", "assistant"]
