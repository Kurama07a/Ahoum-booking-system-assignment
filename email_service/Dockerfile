FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY email_service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY email_service/ .

EXPOSE 5003

CMD ["python", "app.py"]
