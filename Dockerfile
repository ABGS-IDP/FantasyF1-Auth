FROM python:3.13-slim

WORKDIR /app

COPY requirements.dev requirements.txt
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
