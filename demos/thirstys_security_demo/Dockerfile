FROM python:3.11-slim

WORKDIR /app

COPY demo_server.py .
COPY README.md .

RUN pip install flask flask-cors

EXPOSE 5000

CMD ["python", "demo_server.py"]
