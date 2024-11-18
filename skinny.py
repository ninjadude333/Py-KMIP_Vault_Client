import os
import logging
import time
import argparse
from logging.handlers import RotatingFileHandler
from datetime import datetime
from kmip.pie.client import ProxyKmipClient
from kmip.core import enums
import configparser
from cryptography.hazmat.primitives import serialization

# Global Variables for Configuration
CONFIG = {}


def load_config(config_path):
    """Load configuration from a config file."""
    config = configparser.ConfigParser()
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file {config_path} not found!")
    config.read(config_path)
    return {
        "VAULT_KMIP_HOST": config.get("KMIP", "VAULT_KMIP_HOST", fallback="127.0.0.1"),
        "VAULT_KMIP_PORT": config.getint("KMIP", "VAULT_KMIP_PORT", fallback=5696),
        "CERT_PATH": config.get("KMIP", "CERT_PATH", fallback="/app/certs/client.pem"),
        "KEY_PATH": config.get("KMIP", "KEY_PATH", fallback="/app/certs/key.pem"),
        "CA_PATH": config.get("KMIP", "CA_PATH", fallback="/app/certs/vault-ca.pem"),
        "USE_TLS": config.getboolean("KMIP", "USE_TLS", fallback=False),
        "VALIDATE_TLS": config.getboolean("KMIP", "VALIDATE_TLS", fallback=False),
        "LOG_PATH": config.get("GENERAL", "LOG_PATH", fallback="/app/logs/verbose.log"),
        "LOG_FILE_RECYCLE_SIZE": config.getint("GENERAL", "LOG_FILE_RECYCLE_SIZE", fallback=1048576),  # 1 MB
    }


def setup_logging():
    """Set up logging with verbose output."""
    handlers = [logging.StreamHandler()]  # Always log to stdout

    if True:
        os.makedirs(os.path.dirname("/app/logs/verbose.log"), exist_ok=True)
        file_handler = RotatingFileHandler(
            "/app/logs/verbose.log",
            maxBytes=1048576,
            backupCount=5  # Keep up to 5 rotated log files
        )
        handlers.append(file_handler)

    logging.basicConfig(
        level=logging.DEBUG,  # Set to DEBUG for verbose logging
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=handlers
    )

def write_key_to_file(key_bytes, key_storage_path, key_filename, mode="wb"):
            """Write the key to a local file with optional renaming for old keys."""
            try:
              os.makedirs(key_storage_path, exist_ok=True)
              key_file_path = os.path.join(key_storage_path, key_filename)
              logging.info(f"Key will be written to {key_file_path}")
              logging.info(f"Key bytes to write : {key_bytes}")
              logging.info(f"write mode is : {mode}")
              # Write the new key
              with open(key_file_path, mode) as key_file:
                 key_file.write(key_bytes)
              logging.info(f"Key written to {key_file_path}")
            except Exception as e:
               logging.error(f"Failed to write key to file: {e}")

def write_pem_key(key_bytes, key_storage_path, filename, key_type="public"):
    """Convert raw key bytes to PEM format and write to file."""
    try:
        os.makedirs(key_storage_path, exist_ok=True)
        file_path = os.path.join(key_storage_path, filename)
        logging.info(f"Key will be written to {file_path}")
        if key_type == "public":
            pem_key = serialization.load_der_public_key(key_bytes).public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        elif key_type == "private":
            pem_key = serialization.load_der_private_key(
                key_bytes,
                password=None
            ).private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        else:
            raise ValueError(f"Invalid key_type: {key_type}")

        with open(file_path, "wb") as key_file:
            key_file.write(pem_key)

        logging.info(f"{key_type.capitalize()} key written to: {file_path}")
    except Exception as e:
        logging.error(f"Failed to write {key_type} key to file {filename}: {e}")


def test_kmip_login():
    """Test KMIP login to ensure configuration works."""
    logging.info("Starting KMIP login test...")

    try:
        # Initialize KMIP client configuration
#        client_config = {
 #           tls_client_certificate_path: CONFIG["CERT_PATH"],
  #          tls_client_key_path: CONFIG["KEY_PATH"],
   #         tls_ca_certificate_path: CONFIG["CA_PATH"]
    #    }

        # Log the final client configuration
        logging.debug("KMIP client configuration: ")

        # Connect to KMIP server
        logging.info(f"Connecting to KMIP server at ..")
        client = ProxyKmipClient(
            hostname='10.0.101.180',
            port='5696',
            cert='/app/certs/client.pem',
            key='/app/certs/key.pem',
            ca='/app/certs/vault-ca.pem'
        )

        client.open()
        logging.info("Successfully connected to KMIP server.")

        # Step 1: Create a new key
        logging.info("Creating a new symmetric key...")
        new_key_id = client.create(
            enums.CryptographicAlgorithm.AES,
            256,  # Key length in bits
            operation_policy_name="default"
        )
        logging.info(f"New symmetric key created with ID: {new_key_id}")

        # Step 2: Retrieve the newly created key
        logging.info(f"Retrieving new key with ID: {new_key_id}...")
        new_key = client.get(new_key_id)
        # Step 3: Write the new key to a static file
        logging.info(f"Writing new key to static file: ...")
        write_key_to_file(new_key.value, '/app/output', 'app-key.key')
        logging.info(f"Key rotation completed successfully at {datetime.now()}.")

        # generate key/pair
        # Create RSA key pair
        public_key_id, private_key_id = client.create_key_pair(
            algorithm=enums.CryptographicAlgorithm.RSA,
            length=2048,  # Key length in bits
            public_usage_mask=[
              enums.CryptographicUsageMask.ENCRYPT,
              enums.CryptographicUsageMask.VERIFY
            ],
            private_usage_mask=[
              enums.CryptographicUsageMask.DECRYPT,
              enums.CryptographicUsageMask.SIGN
            ]
        )

        logging.info(f"Public key ID: {public_key_id}")
        logging.info(f"Private key ID: {private_key_id}")

        # Retrieve keys
        public_key = client.get(public_key_id)
        private_key = client.get(private_key_id)

        # Write keys to files
        if public_key and private_key:
                write_pem_key(public_key.value, '/app/output' ,"public_key.pem", key_type="public")
                write_pem_key(private_key.value, '/app/output', "private_key.pem", key_type="private")
        else:
           logging.error("Failed to retrieve keys from KMIP server.")# Create RSA key pair

        # Close connection
        logging.info("Closing connection to KMIP server...")
        client.close()
        logging.info("Disconnected from KMIP server.")
    except Exception as e:
        logging.error(f"An error occurred during KMIP login test: {e}")


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="KMIP Login Test Script")
    parser.add_argument(
        "--config",
        type=str,
        default="config.ini",
        help="Path to the configuration file (default: ./config.ini)"
    )
    args = parser.parse_args()

    # Load configuration
    CONFIG = load_config(args.config)

    # Set up logging
    setup_logging()

    # Perform KMIP login test
    test_kmip_login()
