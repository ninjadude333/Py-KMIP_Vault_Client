import configparser
import os
import time
from kmip.pie.client import ProxyKmipClient
from kmip.pie import enums
from datetime import datetime, timedelta
from pathlib import Path

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Extract KMIP and output configuration parameters
server_hostname = config.get('KMIP', 'server_hostname')
server_port = config.getint('KMIP', 'server_port')
cert_path = config.get('KMIP', 'cert_path')
key_path = config.get('KMIP', 'key_path')
ca_path = config.get('KMIP', 'ca_path')

key_output_folder = config.get('OUTPUT', 'key_output_folder')
metadata_file = config.get('OUTPUT', 'metadata_file')
rotation_interval_days = config.getint('OUTPUT', 'rotation_interval_days')

# Ensure the output folder exists
Path(key_output_folder).mkdir(parents=True, exist_ok=True)

def connect_kmip_client():
    """Initialize the KMIP client using the configuration parameters."""
    client = ProxyKmipClient(
        hostname=server_hostname,
        port=server_port,
        certfile=cert_path,
        keyfile=key_path,
        ca_certs=ca_path
    )
    return client

def rotate_key(client):
    """
    Create a new key on Vault KMIP and save it to a file with timestamped
    versioning for rotation.
    """
    # Step 1: Generate a new key
    key_id = client.create(
        cryptographic_algorithm=enums.CryptographicAlgorithm.AES,
        cryptographic_length=256,
        cryptographic_usage_mask=[
            enums.CryptographicUsageMask.ENCRYPT,
            enums.CryptographicUsageMask.DECRYPT
        ]
    )

    # Step 2: Retrieve the key material
    new_key = client.get(key_id)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    key_filename = f"kmip_key_{timestamp}.bin"
    key_path = os.path.join(key_output_folder, key_filename)

    # Step 3: Write the key to a file
    with open(key_path, 'wb') as f:
        f.write(new_key.value)

    # Step 4: Log the key metadata to a file
    with open(metadata_file, 'a') as metadata_file_handle:
        metadata_file_handle.write(f"{timestamp}: Key ID: {key_id}, Key Path: {key_path}\n")

    print(f"Key rotation successful. Key ID {key_id} saved to {key_path}")

    return key_id, key_path

def check_rotation_needed():
    """
    Check if key rotation is needed based on the rotation interval.
    """
    try:
        with open(metadata_file, 'r') as f:
            last_rotation = f.readlines()[-1].split(': ')[0]
        last_rotation_date = datetime.strptime(last_rotation, "%Y%m%d%H%M%S")
        return datetime.now() >= last_rotation_date + timedelta(days=rotation_interval_days)
    except (FileNotFoundError, IndexError):
        # If metadata file doesn't exist or is empty, trigger rotation
        return True

def main():
    # Connect to KMIP server
    with connect_kmip_client() as client:
        # Check if rotation is needed
        if check_rotation_needed():
            rotate_key(client)
        else:
            print("Rotation not needed at this time.")

if __name__ == "__main__":
    main()
