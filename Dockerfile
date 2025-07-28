FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN pip install --no-index --find-links=./wheels -r requirements.txt

CMD ["python", "codex.py"]
