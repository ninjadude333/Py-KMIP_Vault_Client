# KMIP Client with HashiCorp Vault Integration

This project provides a Dockerized Python client for interacting with a KMIP server, such as HashiCorp Vault's KMIP Secrets Engine. The client script (`rotate_kmip_key.py`) fetches KMIP keys, supports key rotation, and saves keys locally for use in services like database encryption.

## Project Structure

The directory structure for this project should look like this:

```
kmip_client/
├── config.ini           # Configuration file with KMIP server details
├── requirements.txt     # Python dependencies
├── setup.py             # (optional) Python packaging file
├── rotate_kmip_key.py   # Main Python script
└── Dockerfile           # Docker build file
```

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
```

- **KMIP Section**:
  - `server_host`: Hostname or IP of the KMIP server.
  - `server_port`: Port for connecting to the KMIP server.
  - `cert_path`, `key_path`, `ca_path`: Paths to the client certificate, client key, and CA certificate for KMIP authentication.

- **OUTPUT Section**:
  - `key_output_folder`: Directory where keys will be saved.
  - `metadata_file`: Path for saving metadata about generated keys.

- **ROTATION Section**:
  - `rotation_interval_days`: Defines how often (in days) keys should be rotated.

## Dependency Installation: `requirements.txt`
Create a `requirements.txt` file with the following content:

```plaintext
# requirements.txt

pymip==0.10.0
configparser==5.3.0
```

## Optional: `setup.py` for Python Packaging
Create a `setup.py` file to specify dependencies and the required Python version:

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="kmip_client",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        "pymip==0.10.0",
        "configparser==5.3.0"
    ],
    python_requires=">=3.6",
)
```

## Main Script: `rotate_kmip_key.py`
Create the main script, `rotate_kmip_key.py`, to interact with the KMIP server and handle key rotation and file output.

```python
# rotate_kmip_key.py
import configparser
import datetime
from pathlib import Path
from kmip.pie import client

def load_config():
    config = configparser.ConfigParser()
    config.read('/app/config.ini')
    return config

def get_kmip_key(kmip_client, key_id):
    return kmip_client.get(key_id)

def write_key_to_disk(key, output_folder, metadata_file):
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    key_path = output_folder / f"key_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.key"

    with open(key_path, 'wb') as f:
        f.write(key)
    
    with open(metadata_file, 'a') as meta:
        meta.write(f"{datetime.datetime.now()}: Key {key_path.name} stored\n")

def rotate_key_if_needed(config, kmip_client):
    last_rotation = config.get('ROTATION', 'last_rotation', fallback=None)
    rotation_interval_days = int(config['ROTATION']['rotation_interval_days'])

    if last_rotation:
        last_rotation_date = datetime.datetime.strptime(last_rotation, '%Y-%m-%d')
        if (datetime.datetime.now() - last_rotation_date).days < rotation_interval_days:
            return False
    
    key_id = config['KMIP'].get('key_id')
    key = get_kmip_key(kmip_client, key_id)
    write_key_to_disk(key, config['OUTPUT']['key_output_folder'], config['OUTPUT']['metadata_file'])
    
    config['ROTATION']['last_rotation'] = datetime.datetime.now().strftime('%Y-%m-%d')
    with open('/app/config.ini', 'w') as configfile:
        config.write(configfile)
    return True

def main():
    config = load_config()
    kmip_client = client.ProxyKmipClient(
        hostname=config['KMIP']['server_host'],
        port=int(config['KMIP']['server_port']),
        cert=config['KMIP']['cert_path'],
        key=config['KMIP']['key_path'],
        ca=config['KMIP']['ca_path']
    )
    with kmip_client:
        rotated = rotate_key_if_needed(config, kmip_client)
        if rotated:
            print("Key rotated and stored successfully.")
        else:
            print("Rotation not needed yet.")

if __name__ == "__main__":
    main()
```

## Dockerfile
Create a `Dockerfile` to define the Docker image:

```Dockerfile
# Dockerfile
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Environment variable for config file path
ENV CONFIG_FILE_PATH="/app/config.ini"

# Define entrypoint to run the script with the configuration file
ENTRYPOINT ["python", "rotate_kmip_key.py"]
```

## Building and Running the Docker Container

### Step 1: Build the Docker Image
Run the following command from the `kmip_client` directory:

```bash
docker build -t kmip-client .
```

### Step 2: Run the Docker Container
To run the client, you need to:
- Mount the `config.ini` file to provide configuration details.
- Mount an output directory for storing keys and metadata generated by the client.

```bash
docker run --rm \
  -v $(pwd)/config.ini:/app/config.ini \
  -v $(pwd)/output:/app/output \
  kmip-client
```

- **config.ini**: This file should be mounted as `/app/config.ini` inside the container.
- **Output Directory**: The `/app/output` directory will store output files. You may customize paths in the `config.ini` to ensure output files are saved in the mounted `output` folder.

## Example Usage
The client script:
1. Connects to the KMIP server using the provided credentials.
2. Retrieves the current KMIP key.
3. Saves the key to the specified output directory.
4. Manages key rotation based on the defined interval.

This setup is ideal for applications like database encryption at rest, where KMIP key rotation is triggered by the client.

## Additional Notes
For local development and testing:
- Ensure Python 3.8+ is installed.
- Install dependencies using `requirements.txt`.

## License
This project is licensed under the MIT License.
```

This `README.md` file provides complete documentation, including setup, configuration, Docker build instructions, and usage details.