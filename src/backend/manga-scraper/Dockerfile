FROM python:3.10.12-slim

WORKDIR /app

COPY build_requirements.txt .

RUN pip install --no-cache-dir -r build_requirements.txt

COPY . .

CMD ["python3", "scraper.py"]
