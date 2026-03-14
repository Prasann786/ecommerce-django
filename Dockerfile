
FROM python:3.11

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Run Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]