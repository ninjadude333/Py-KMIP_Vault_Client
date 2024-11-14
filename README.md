# KMIP Client with HashiCorp Vault Integration

This project provides a Dockerized Python client for interacting with a KMIP server, such as HashiCorp Vault's KMIP Secrets Engine. The client script (`rotate_kmip_key.py`) fetches KMIP keys, supports key rotation, and saves keys locally for use in services like database encryption.

## Project Structure

The directory structure for this project should look like this:
kmip_client/ ├── config.ini # Configuration file with KMIP server details ├── requirements.txt # Python dependencies ├── setup.py # (optional) Python packaging file ├── rotate_kmip_key.py # Main Python script └── Dockerfile # Docker build file


### File Descriptions
- **`config.ini`**: Configuration file specifying KMIP server details, output paths, and rotation settings.
- **`requirements.txt`**: List of required Python packages.
- **`setup.py`**: (Optional) Python setup file for specifying dependencies and Python version.
- **`rotate_kmip_key.py`**: Main Python script that connects to the KMIP server, retrieves keys, rotates keys if necessary, and saves them locally.
- **`Dockerfile`**: Dockerfile for creating a containerized environment to run the script.

## Configuration: `config.ini`
Create a `config.ini` file in the project directory with the following content:

```ini
# config.ini
[KMIP]
server_host = "your-kmip-server-host"
server_port = "5696"
cert_path = "/path/to/cert.pem"
key_path = "/path/to/key.pem"
ca_path = "/path/to/ca.pem"

[OUTPUT]
key_output_folder = "/app/output"
metadata_file = "/app/output/key_metadata.txt"

[ROTATION]
rotation_interval_days = 90

KMIP Section:

server_host: Hostname or IP of the KMIP server.
server_port: Port for connecting to the KMIP server.
cert_path, key_path, ca_path: Paths to the client certificate, client key, and CA certificate for KMIP authentication.
OUTPUT Section:

key_output_folder: Directory where keys will be saved.
metadata_file: Path for saving metadata about generated keys.
ROTATION Section:

rotation_interval_days: Defines how often (in days) keys should be rotated.

Building and Running the Docker Container
Step 1: Build the Docker Image
Run the following command from the kmip_client directory:

bash
Copy code
docker build -t kmip-client .
Step 2: Run the Docker Container
To run the client, you need to:

Mount the config.ini file to provide configuration details.
Mount an output directory for storing keys and metadata generated by the client.
bash
Copy code
docker run --rm \
  -v $(pwd)/config.ini:/app/config.ini \
  -v $(pwd)/output:/app/output \
  kmip-client
config.ini: This file should be mounted as /app/config.ini inside the container.
Output Directory: The /app/output directory will store output files. You may customize paths in the config.ini to ensure output files are saved in the mounted output folder.
Example Usage
The client script:

Connects to the KMIP server using the provided credentials.
Retrieves the current KMIP key.
Saves the key to the specified output directory.
Manages key rotation based on the defined interval.
This setup is ideal for applications like database encryption at rest, where KMIP key rotation is triggered by the client.

Additional Notes
For local development and testing:

Ensure Python 3.8+ is installed.
Install dependencies using requirements.txt.
License
This project is licensed under the MIT License.


This `README.md` file provides complete documentation, including setup, configuration, Docker build instructions, and usage details.
