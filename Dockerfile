# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Copy only the necessary files and directories
COPY common/*.py /app/common/
COPY data_fetcher/*.json /app/data_fetcher/
COPY data_fetcher/*.py /app/data_fetcher/
COPY data_layer/*.py /app/data_layer/
COPY movies_service/*.py /app/movies_service/
COPY movies_service/oas.yaml /app/movies_service/
COPY movies_service/api/*.py /app/movies_service/api/
COPY migrations/*.py /app/migrations/
COPY migrations/versions/*.py /app/migrations/versions/
COPY requirements.txt /app/movies_service/
COPY alembic.ini /app/


# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /app/movies_service/requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD ["uvicorn", "movies_service.app:app", "--host", "0.0.0.0", "--port", "8000"]