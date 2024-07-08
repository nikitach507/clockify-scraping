FROM ubuntu:20.04

RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.10 \
    python3.10-venv \
    python3.10-dev \
    python3-pip \
    && apt-get clean

RUN pip3 install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create false \
    && poetry install --no-root

RUN pip3 install python-dotenv 

COPY . /app

ENV PYTHONPATH "${PYTHONPATH}:/app"

CMD ["python3.10", "clockify_scraping/main.py"]

