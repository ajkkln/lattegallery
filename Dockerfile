FROM python:3.12-alpine AS install

WORKDIR /lattegallery

COPY install-poetry.py .
ENV PATH="$PATH:/root/.local/bin"
RUN chmod +x install-poetry.py && \
    python3 install-poetry.py --version 1.8.2 && \
    rm install-poetry.py && \
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry install -n --no-cache --no-root


FROM install AS run

COPY lattegallery/ lattegallery/

EXPOSE 8080

ENTRYPOINT [ "sh", "-c", "python -m uvicorn --port $SERVER_PORT --host 0.0.0.0 --root-path $ROOT_PATH lattegallery.main:app" ]
