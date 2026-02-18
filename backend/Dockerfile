FROM python:3.9-slim

# Create non-root user early
RUN useradd -m appuser

WORKDIR /app

# Copy only requirements first (better layer caching)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy only required app files
COPY app.py .
COPY src/ ./src/

# Switch to non-root user
USER appuser

EXPOSE 5000

CMD ["python", "app.py"]

