# =================================================================
# This script is the heart of our generic container. It's responsible
# for fetching the actual application logic and configuration from GCS.
# =================================================================
# Exit immediately if a command exits with a non-zero status.
set -e

# Check if the correct number of arguments (GCS paths) are provided.
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <gcs_path_to_script> <gcs_path_to_config>"
    exit 1
fi

# Assign the arguments to variables for clarity.
GCS_SCRIPT_PATH=$1
GCS_CONFIG_PATH=$2
LOCAL_SCRIPT_PATH="/app/publisher.py"
LOCAL_CONFIG_PATH="/app/config.json"
VENV_PYTHON="/app/venv/bin/python3"

echo "--- GKE Publisher Runner (VENV) ---"
echo "Fetching Python script from: ${GCS_SCRIPT_PATH}"
echo "Fetching config file from: ${GCS_CONFIG_PATH}"

# Use gsutil to copy the files from GCS to the local filesystem.
gsutil cp "${GCS_SCRIPT_PATH}" "${LOCAL_SCRIPT_PATH}"
gsutil cp "${GCS_CONFIG_PATH}" "${LOCAL_CONFIG_PATH}"

echo "Files downloaded successfully."
echo "---------------------------------"

# Execute the downloaded Python script using the Python interpreter
# from the virtual environment.
${VENV_PYTHON} "${LOCAL_SCRIPT_PATH}" --config "${LOCAL_CONFIG_PATH}"