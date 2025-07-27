# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the working directory
COPY . .

# Command to run the application (replace your_script_name.py with the actual script name)
# This assumes your main trading logic is in a file named trading_agent.main.py
CMD ["python", "trading_agent.main.py"]
