# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory to /app/src
WORKDIR /app/src

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Command to run on container start
CMD ["python", "main.py"]