# Use official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy local code to the container
COPY . /app

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create cache directories for ChromaDB/FastEmbed and give permission
# (Hugging Face runs as a non-root user usually user 1000)
RUN mkdir -p /app/chroma_db_store /app/model_cache && \
    chmod -R 777 /app/chroma_db_store /app/model_cache

# Expose port 7860 (Hugging Face default)
EXPOSE 7860

# Run FastAPI
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7860"]