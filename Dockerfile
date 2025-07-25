# 1) Base image
FROM python:3.12-slim

# 2) Set work directory
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3) Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Copy project files
COPY . .


# 5) Expose FastAPI port
EXPOSE 8000

# 6) Run app with Uvicorn
CMD ["uvicorn", "telegram_bot.main:app", "--host", "0.0.0.0", "--port", "8000"]
