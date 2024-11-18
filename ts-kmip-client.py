import os
import time
import logging
from logging.handlers import RotatingFileHandler
import schedule
from datetime import datetime
from kmip.pie.client import ProxyKmipClient
from kmip.core import enums
import configparser


# Global Variables for Configuration
CONFIG = {}
DEFAULT_CONFIG_PATH = "config.ini"


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
        "USE_TLS": config.getboolean("KMIP", "USE_TLS", fallback=True),
        "VALIDATE_TLS": config.getboolean("KMIP", "VALIDATE_TLS", fallback=True),
        "KEY_STORAGE_PATH": config.get("GENERAL", "KEY_STORAGE_PATH", fallback="/app/output"),
        "STATIC_KEY_FILENAME": config.get("GENERAL", "STATIC_KEY_FILENAME", fallback="app-key.key"),
        "ROTATION_PERIOD_HOURS": config.getint("GENERAL", "ROTATION_PERIOD_HOURS", fallback=24),
        "KEEP_OLD_KEY": config.getboolean("GENERAL", "KEEP_OLD_KEY", fallback=False),
        "KEEP_NUM_KEYS": config.getint("GENERAL", "KEEP_NUM_KEYS", fallback=5),
        "LOG_PATH": config.get("GENERAL", "LOG_PATH", fallback="/app/logs/rotation.log"),
        "LOG_FILE_RECYCLE_SIZE": config.getint("GENERAL", "LOG_FILE_RECYCLE_SIZE", fallback=1048576),  # 1 MB
        "WRITE_TO_LOG_FILE": config.getboolean("GENERAL", "WRITE_TO_LOG_FILE", fallback=True),
        "ENABLE_PERIODIC_ROTATION": config.getboolean("GENERAL", "ENABLE_PERIODIC_ROTATION", fallback=True),
    }


def setup_logging():
    """Set up logging with optional file recycling."""
    handlers = [logging.StreamHandler()]  # Always log to stdout

    if CONFIG["WRITE_TO_LOG_FILE"]:
        os.makedirs(os.path.dirname(CONFIG["LOG_PATH"]), exist_ok=True)
        file_handler = RotatingFileHandler(
            CONFIG["LOG_PATH"],
            maxBytes=CONFIG["LOG_FILE_RECYCLE_SIZE"],
            backupCount=5  # Keep up to 5 rotated log files
        )
        handlers.append(file_handler)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=handlers
    )


def write_key_to_file(key_bytes, key_storage_path, key_filename):
    """Write the key to a local file with optional renaming for old keys."""
    try:
        os.makedirs(key_storage_path, exist_ok=True)
        key_file_path = os.path.join(key_storage_path, key_filename)

        # If KEEP_OLD_KEY is enabled, rename the old key
        if CONFIG["KEEP_OLD_KEY"] and os.path.exists(key_file_path):
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            old_key_file_path = os.path.join(
                key_storage_path, f"{key_filename}.{timestamp}"
            )
            os.rename(key_file_path, old_key_file_path)
            logging.info(f"Old key renamed to: {old_key_file_path}")

            # Enforce KEEP_NUM_KEYS limit
            enforce_key_retention_limit(key_storage_path, key_filename)

        # Write the new key
        with open(key_file_path, "wb") as key_file:
            key_file.write(key_bytes)
        logging.info(f"Key written to {key_file_path}")
    except Exception as e:
        logging.error(f"Failed to write key to file: {e}")


def enforce_key_retention_limit(key_storage_path, key_filename):
    """Ensure the number of old keys does not exceed KEEP_NUM_KEYS."""
    try:
        all_keys = [
            f for f in os.listdir(key_storage_path)
            if f.startswith(key_filename) and f != key_filename
        ]
        all_keys.sort(reverse=True)  # Sort by most recent timestamp

        # Remove excess keys
        for old_key in all_keys[CONFIG["KEEP_NUM_KEYS"]:]:
            os.remove(os.path.join(key_storage_path, old_key))
            logging.info(f"Removed old key: {old_key}")
    except Exception as e:
        logging.error(f"Failed to enforce key retention limit: {e}")


def perform_key_rotation():
    """Perform key rotation: destroy the old key and create a new one."""
    logging.info("Starting key rotation process...")

    try:
        # Initialize KMIP client configuration
        client_config = {
            'use_tls': CONFIG["USE_TLS"],
            'tls_client_certificate_path': CONFIG["CERT_PATH"],
            'tls_client_key_path': CONFIG["KEY_PATH"],
            'tls_ca_certificate_path': CONFIG["CA_PATH"],
            'validate_tls': CONFIG["VALIDATE_TLS"]
        }

        if not client_config["use_tls"]:
            # Disable all TLS settings for HTTP connections
            client_config = {}

        client = ProxyKmipClient(
            hostname=CONFIG["VAULT_KMIP_HOST"],
            port=CONFIG["VAULT_KMIP_PORT"],
            config=client_config
        )

        client.open()
        logging.info("Connected to Vault KMIP secrets engine.")

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
        logging.info(f"Writing new key to static file: {CONFIG['STATIC_KEY_FILENAME']}...")
        write_key_to_file(new_key, CONFIG["KEY_STORAGE_PATH"], CONFIG["STATIC_KEY_FILENAME"])

        logging.info(f"Key rotation completed successfully at {datetime.now()}.")

    except Exception as e:
        logging.error(f"An error occurred during key rotation: {e}")

    finally:
        if 'client' in locals():
            client.close()
            logging.info("Disconnected from Vault KMIP secrets engine.")
        else:
            logging.warning("KMIP client was not initialized. Skipping disconnection.")


def schedule_key_rotation():
    """Schedule periodic key rotations."""
    logging.info(f"Scheduling key rotation every {CONFIG['ROTATION_PERIOD_HOURS']} hours...")
    schedule.every(CONFIG["ROTATION_PERIOD_HOURS"]).hours.do(perform_key_rotation)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    # Load configuration
    CONFIG = load_config(DEFAULT_CONFIG_PATH)

    # Set up logging
    setup_logging()

    # Perform an initial key rotation immediately
    logging.info("Performing initial key rotation...")
    perform_key_rotation()

    # Enable periodic rotations if configured
    if CONFIG["ENABLE_PERIODIC_ROTATION"]:
        schedule_key_rotation()
    else:
        logging.info("Periodic rotation is disabled. Exiting after the initial rotation.")
