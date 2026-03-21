FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY core/ ./core/
COPY templates/ ./templates/
COPY packs/ ./packs/

ENV TPS_HOST=0.0.0.0
ENV TPS_PORT=8080

EXPOSE 8080

CMD ["uvicorn", "core.app:app", "--host", "0.0.0.0", "--port", "8080"]
