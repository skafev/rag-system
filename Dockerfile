# -------------------------------
# Step 1: Base image
# -------------------------------
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# -------------------------------
# Step 2: Set working directory
# -------------------------------
WORKDIR /app

# -------------------------------
# Step 3: Copy requirements & install dependencies
# -------------------------------
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m nltk.downloader punkt punkt_tab
# -------------------------------
# Step 4: Copy project files
# -------------------------------
COPY . .

# -------------------------------
# Step 5: Expose port
# -------------------------------
EXPOSE 8000

# -------------------------------
# Step 6: Start the FastAPI server
# -------------------------------
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
