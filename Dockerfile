# ---- Small, repeatable image for the To-Do API ----
FROM python:3.12-slim

# Do not write .pyc files; print logs straight to the terminal
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first: this layer is cached until requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app ./app
COPY wsgi.py .

# Run as a normal user, not root
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

# Container is "healthy" only if the API (and its database) answer
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "wsgi:app"]
