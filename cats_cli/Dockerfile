
FROM python:3.13-slim

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry install --no-root 

COPY . /app/


CMD ["poetry", "run", "python", "main.py"]
