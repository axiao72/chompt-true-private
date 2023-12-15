# === Build Stage ===
FROM python:3.11 as build

# Install Node.js and npm for the build stage
RUN apt-get update && \
    apt-get install -y nodejs npm vim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install npm packages
RUN npm install --force
RUN npm audit fix --force

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

CMD ["npm", "run", "dev"]