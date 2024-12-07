# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory to /app/src
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Set the Python path to include the app root
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Command to run on container start
ENTRYPOINT ["python", "src/main.py"]