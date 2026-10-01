# The web calculator and API. Most hosts (Render, Fly.io, Railway) set $PORT.
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir ".[api]"
ENV PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "uvicorn lk_tax.api:app --host 0.0.0.0 --port ${PORT}"]
