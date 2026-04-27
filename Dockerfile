# Use official Python 3.12 image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose the port Flet will run on (Render sets PORT env variable)
EXPOSE 8000

# Start the app using flet's built-in webserver
CMD flet run --web main.py --port $PORT
