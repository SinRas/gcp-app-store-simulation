# =================================================================
# This file defines how to build our generic runner container.
# We use the google/cloud-sdk base image because it already has
# tools like 'gsutil' installed, which we'll use to download files.
# =================================================================
FROM google/cloud-sdk:slim

# Set the working directory inside the container
WORKDIR /app

# Install Python, venv, and the dos2unix utility to fix line endings
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv dos2unix && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Define the path for the virtual environment as an environment variable
ENV VENV_PATH=/app/venv

# Create the virtual environment
RUN python3 -m venv ${VENV_PATH}

# Install the required Python libraries INTO the virtual environment
RUN ${VENV_PATH}/bin/pip install --no-cache-dir --upgrade pip && \
    ${VENV_PATH}/bin/pip install --no-cache-dir google-cloud-pubsub \
        faker google-cloud-storage numpy numba pytz

# Copy the entrypoint script into the container
COPY entrypoint.sh .

# --- Possible prevention of error 'exec format error' ---
# Convert the entrypoint script from DOS/Windows line endings to Unix line endings.
RUN dos2unix /app/entrypoint.sh

# Make the script executable
RUN chmod +x entrypoint.sh

# This is the command that will run when the container starts
ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]