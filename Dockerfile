FROM python:3.10-slim

# Main folder layer
WORKDIR /code
# Copy and install dependicies
COPY requirements.txt .
RUN pip install -r requirements.txt
# Copy project to image
COPY . /code


ENV DEBUG=TRUE
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
