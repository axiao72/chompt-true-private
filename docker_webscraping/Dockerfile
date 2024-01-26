# === Build Stage ===
FROM python:3.11 as build

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install Python packages
RUN pip install --no-cache-dir -r requirements_webscraping.txt

CMD ["python3", "updating_with_location_data.py"]