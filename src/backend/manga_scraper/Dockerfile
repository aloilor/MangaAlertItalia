FROM python:3.10.12-slim

WORKDIR /app

COPY build_requirements.txt .
COPY . .

RUN pip install --no-cache-dir -r build_requirements.txt


CMD ["python3", "main.py"]
