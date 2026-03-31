FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create reports directory
RUN mkdir -p reports config

# Default: run morning routine
CMD ["python", "autonomous.py", "morning"]
