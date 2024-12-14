# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make the script executable
RUN chmod +x /app/rocket_chat.py


# Run the script
CMD ["python", "rocket_chat.py"]

