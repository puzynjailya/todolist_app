FROM python:3.10-slim

# Main folder layer
WORKDIR /app
# Copy and install dependicies
COPY requirements.txt .
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install -r requirements.txt --no-cache-dir
# Copy project to image
COPY app /app

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
