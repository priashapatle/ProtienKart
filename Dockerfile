FROM python:3.12-slim

WORKDIR /app

# Copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py server.py
COPY .env .

# Expose port
EXPOSE 8080

# Run server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]