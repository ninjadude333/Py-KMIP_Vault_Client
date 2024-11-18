Here’s the updated `README.md` file including networking and other requirements for running the KMIP Key Management Client.

---

# KMIP Key Management Client

This project provides a Python-based KMIP (Key Management Interoperability Protocol) client for managing cryptographic keys through a KMIP server such as HashiCorp Vault. It supports features like periodic key rotation, retention of old keys, static filenames for seamless integration, and log file rotation.

---

## Features

- **Periodic Key Rotation**:
  Automatically rotates keys at a configurable interval.
- **Manual Key Creation**:
  Supports on-demand key creation via a single run.
- **Key Retention**:
  Retains a specified number of old keys for reference or backup.
- **Static Key Filename**:
  Always writes the current key to a static filename for seamless application use.
- **Log File Rotation**:
  Prevents log file bloat by recycling logs when they reach a configured size.

---

## Requirements

### Networking Requirements

1. **KMIP Server Connectivity**:
   - Ensure the container or host running the client has network access to the KMIP server.
   - The default port for KMIP is **5696** (can be customized via `config.ini`).

2. **Firewall Rules**:
   - Allow outbound traffic from the client to the KMIP server on the specified port.
   - Ensure the KMIP server can respond to incoming requests from the client.

3. **TLS/SSL**:
   - TLS/SSL is required for secure communication with the KMIP server.
   - Certificates and keys are needed for mutual TLS authentication.

4. **DNS or IP**:
   - The KMIP server hostname or IP address must be resolvable and reachable.

### System Requirements

1. **Operating System**:
   - The client is designed to run in a Docker container, but it can also be executed directly on Linux, macOS, or Windows systems with Python installed.

2. **Python**:
   - Python version **3.10** or higher is required if running locally.

3. **Dependencies**:
   - Install the required Python packages using `requirements.txt`:
     ```bash
     pip install -r requirements.txt
     ```

4. **Certificates**:
   - The following certificates and keys are required for mutual TLS authentication:
     - **Client Certificate (`client.crt`)**: Issued by the KMIP server's CA.
     - **Client Key (`client.key`)**: Private key corresponding to the client certificate.
     - **CA Certificate (`ca.pem`)**: The KMIP server's certificate authority certificate.

5. **Disk Space**:
   - Ensure there is sufficient disk space for:
     - Logs in `/app/logs` (log rotation will manage size).
     - Keys in `/app/output`.

---

## Configuration

All configurations are managed via a `config.ini` file.

### Example `config.ini`:

```ini
[KMIP]
VAULT_KMIP_HOST=127.0.0.1
VAULT_KMIP_PORT=5696
CERT_PATH=/app/certs/client.crt
KEY_PATH=/app/certs/client.key
CA_PATH=/app/certs/ca.pem

[GENERAL]
KEY_STORAGE_PATH=/app/output
STATIC_KEY_FILENAME=app-key.key
ROTATION_PERIOD_HOURS=24
KEEP_OLD_KEY=true
KEEP_NUM_KEYS=5
LOG_PATH=/app/logs/rotation.log
LOG_FILE_RECYCLE_SIZE=1048576  # 1 MB in bytes
WRITE_TO_LOG_FILE=true
ENABLE_PERIODIC_ROTATION=true
```

### Configuration Parameters

| Section       | Parameter                 | Description                                                                 |
|---------------|---------------------------|-----------------------------------------------------------------------------|
| **[KMIP]**    | `VAULT_KMIP_HOST`         | KMIP server hostname or IP address.                                        |
|               | `VAULT_KMIP_PORT`         | KMIP server port (default is `5696`).                                      |
|               | `CERT_PATH`               | Path to the client certificate for authentication.                         |
|               | `KEY_PATH`                | Path to the client private key for authentication.                         |
|               | `CA_PATH`                 | Path to the CA certificate for authentication.                             |
| **[GENERAL]** | `KEY_STORAGE_PATH`        | Directory where keys are stored.                                           |
|               | `STATIC_KEY_FILENAME`     | The name of the current key file (e.g., `app-key.key`).                    |
|               | `ROTATION_PERIOD_HOURS`   | Interval in hours for periodic key rotation.                               |
|               | `KEEP_OLD_KEY`            | If `true`, renames old keys with a timestamp.                              |
|               | `KEEP_NUM_KEYS`           | Maximum number of old keys to retain.                                      |
|               | `LOG_PATH`                | Path to the log file.                                                      |
|               | `LOG_FILE_RECYCLE_SIZE`   | Maximum size of the log file in bytes before recycling.                    |
|               | `WRITE_TO_LOG_FILE`       | If `true`, writes logs to a file in addition to `stdout`.                  |
|               | `ENABLE_PERIODIC_ROTATION`| If `true`, enables periodic rotation. Otherwise, runs once and exits.      |

---

## Running with Docker

### 1. Build the Docker Image

```bash
docker build -t kmip-client-rotation .
```

### 2. Running as a Periodic Job

To set up periodic key rotation:

```bash
docker run -d \
    --name kmip-rotation-job \
    -v /path/to/certs:/app/certs \
    -v /path/to/output:/app/output \
    -v /path/to/logs:/app/logs \
    -v /path/to/config.ini:/app/config.ini \
    kmip-client-rotation
```

### 3. Running for Manual Key Creation

To create a key manually:

```bash
docker run --rm \
    -v /path/to/certs:/app/certs \
    -v /path/to/output:/app/output \
    -v /path/to/logs:/app/logs \
    -v /path/to/config.ini:/app/config.ini \
    kmip-client-rotation python ts-kmip-client.py
```

---

## Logs

### Viewing Logs in Docker

Use the following command to view logs in real-time:

```bash
docker logs kmip-rotation-job
```

### Log Rotation

Logs are automatically recycled when they exceed the size specified in `LOG_FILE_RECYCLE_SIZE`. Up to 5 backup log files are retained.

---

## Key Management

### Directory Structure

After running the container, the output directory (`/app/output` by default) will contain:

- **Latest Key**:
  - File: `app-key.key`
  - Contains the current key material.

- **Old Keys** (if `KEEP_OLD_KEY=true`):
  - Files: `app-key.key.<timestamp>` (e.g., `app-key.key.20241117120000`).
  - Number of old keys retained is determined by `KEEP_NUM_KEYS`.

---

## Customization

### Change Key Rotation Interval

Modify the `ROTATION_PERIOD_HOURS` parameter in `config.ini` to change the interval for periodic rotation.

### Limit Old Keys

Set `KEEP_NUM_KEYS` in `config.ini` to control how many old keys are retained.

### Control Log File Size

Adjust `LOG_FILE_RECYCLE_SIZE` in `config.ini` to set the maximum size of the log file in bytes before recycling.

---

## Stopping the Periodic Job

To stop the periodic job:

```bash
docker stop kmip-rotation-job
docker rm kmip-rotation-job
```

---

## Development and Testing

### Running Locally with Python

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the script:
   ```bash
   python ts-kmip-client.py
   ```

### Running in VSCode

Use the provided `.vscode/launch.json` to debug and test the script in VSCode.

---

## Contributing

Feel free to fork this repository and submit pull requests. For major changes, please open an issue to discuss your ideas.

---

## License

This project is licensed under the MIT License. See `LICENSE` for details.

---

## Author

This project was developed to simplify cryptographic key management for applications requiring seamless key updates and rotation.

---

This comprehensive `README.md` file includes system, networking, and configuration requirements to ensure proper setup and operation.


To convert the raw key bytes to a standard PEM format, you can use the `cryptography` library in Python. This will encode the keys with the necessary headers and Base64-encoded content.

Below is the enhanced example that converts the raw keys to PEM format and writes them to files:

---

### Enhanced Example: Convert and Write Keys in PEM Format

```python
import os
from kmip.pie.client import ProxyKmipClient
from kmip.core import enums
from cryptography.hazmat.primitives import serialization

# Configuration for KMIP connection
kmip_config = {
    'hostname': '127.0.0.1',  # Replace with your KMIP server address
    'port': 5696,             # Replace with your KMIP server port
    'use_tls': True,
    'tls_client_certificate_path': 'path/to/client.pem',
    'tls_client_key_path': 'path/to/key.pem',
    'tls_ca_certificate_path': 'path/to/ca.pem',
    'validate_tls': True
}

output_dir = "keys"  # Directory where the key files will be saved


def write_pem_key(key_bytes, filename, key_type="public"):
    """Convert raw key bytes to PEM format and write to file."""
    try:
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, filename)

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

        print(f"{key_type.capitalize()} key written to: {file_path}")
    except Exception as e:
        print(f"Failed to write {key_type} key to file {filename}: {e}")


def create_key_pair_example():
    """Create an asymmetric key pair using KMIP and write to PEM files."""
    try:
        # Initialize KMIP client
        client = ProxyKmipClient(
            hostname=kmip_config["hostname"],
            port=kmip_config["port"],
            use_tls=kmip_config["use_tls"],
            tls_client_certificate_path=kmip_config["tls_client_certificate_path"],
            tls_client_key_path=kmip_config["tls_client_key_path"],
            tls_ca_certificate_path=kmip_config["tls_ca_certificate_path"],
            validate_tls=kmip_config["validate_tls"]
        )

        client.open()
        print("Connected to KMIP server.")

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

        print(f"Public key ID: {public_key_id}")
        print(f"Private key ID: {private_key_id}")

        # Retrieve keys
        public_key = client.get(public_key_id)
        private_key = client.get(private_key_id)

        # Write keys to PEM files
        if public_key and private_key:
            write_pem_key(public_key.value, "public_key.pem", key_type="public")
            write_pem_key(private_key.value, "private_key.pem", key_type="private")
        else:
            print("Failed to retrieve keys from KMIP server.")

        client.close()
        print("Disconnected from KMIP server.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Run the example
create_key_pair_example()
```

---

### Key Updates:

1. **Convert Keys to PEM Format**:
   - For **public keys**:
     - `serialization.load_der_public_key` converts the raw DER format to a public key object.
     - `.public_bytes` encodes it in PEM format with `SubjectPublicKeyInfo`.
   - For **private keys**:
     - `serialization.load_der_private_key` converts the raw DER format to a private key object.
     - `.private_bytes` encodes it in PEM format with PKCS8.

2. **Write Keys to Files**:
   - Keys are saved in the `keys` directory as `public_key.pem` and `private_key.pem`.

---

### Installing `cryptography`
You need the `cryptography` library to run this script. Install it with:

```bash
pip install cryptography
```

---

### Example Output Files:
#### **`public_key.pem`**:
```plaintext
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAr7zz3/HFjYozZ2Z/kM9u
...
-----END PUBLIC KEY-----
```

#### **`private_key.pem`**:
```plaintext
-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCur7zz3/HFjYoz
...
-----END PRIVATE KEY-----
```

---

### Notes:
- Use `openssl` to validate the keys:
  - **Check the public key**:
    ```bash
    openssl rsa -pubin -in keys/public_key.pem -text -noout
    ```
  - **Check the private key**:
    ```bash
    openssl rsa -in keys/private_key.pem -check -noout
    ```

- Adjust key formats (e.g., PKCS1) if needed by changing the parameters in `.public_bytes` or `.private_bytes`.


When saving a **symmetric key**, you can serialize it for better interoperability, readability, or future use cases, just as you do with public/private keys. Simply writing the raw binary data to a file works, but serialization provides additional benefits, such as ensuring the format adheres to cryptographic standards and is easier to validate or exchange across systems.

Here’s how you can handle symmetric keys effectively:

---

### **Serialization for Symmetric Keys**
#### **Why Serialize Symmetric Keys?**
- **Readability**: Serialized keys can be Base64-encoded, making them easier to view and validate without risking corruption.
- **Portability**: Serialized keys follow a specific format, making them easier to use across systems.
- **Validation**: You can include metadata like the algorithm and key size for self-validation.

#### **Serialize Symmetric Key to Base64**
Here’s how to serialize the symmetric key into a PEM-like format:
```python
import base64

def serialize_symmetric_key(key_bytes, algorithm="AES"):
    """Serialize symmetric key to a Base64-encoded format."""
    header = f"-----BEGIN {algorithm} KEY-----\n"
    footer = f"\n-----END {algorithm} KEY-----"
    # Encode the key in Base64 and wrap lines at 64 characters
    key_b64 = base64.encodebytes(key_bytes).decode("utf-8")
    key_wrapped = "\n".join(key_b64[i:i+64] for i in range(0, len(key_b64), 64))
    return f"{header}{key_wrapped}{footer}"
```

#### **Write Serialized Key to File**
```python
def write_serialized_symmetric_key(key_bytes, filename):
    """Serialize and write symmetric key to a file."""
    try:
        serialized_key = serialize_symmetric_key(key_bytes)
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, filename)
        with open(file_path, "w") as key_file:
            key_file.write(serialized_key)
        print(f"Serialized symmetric key written to: {file_path}")
    except Exception as e:
        print(f"Failed to write serialized symmetric key to file {filename}: {e}")
```

---

### **Validating a Symmetric Key**
Validation ensures that the key conforms to expected properties like size and usage. Here’s how you can validate a symmetric key:

#### **Validation Example**
```python
def validate_symmetric_key(key_bytes, expected_algorithm="AES", expected_length=256):
    """Validate the properties of a symmetric key."""
    if len(key_bytes) * 8 != expected_length:
        raise ValueError(f"Invalid key length: Expected {expected_length} bits, got {len(key_bytes) * 8} bits")
    print(f"Key is valid for {expected_algorithm} with length {expected_length} bits.")
```

#### **Usage in the Workflow**
1. **Generate or Retrieve the Key**:
   - Use your KMIP client to generate or retrieve the key as raw bytes.
2. **Validate the Key**:
   ```python
   validate_symmetric_key(key_bytes, expected_algorithm="AES", expected_length=256)
   ```
3. **Serialize and Save**:
   ```python
   write_serialized_symmetric_key(key_bytes, "symmetric_key.pem")
   ```

---

### **Complete Workflow Example**

```python
def handle_symmetric_key(key_id, client):
    """Retrieve, validate, serialize, and write a symmetric key."""
    try:
        # Retrieve the key
        key = client.get(key_id)
        if hasattr(key, 'value'):
            key_bytes = key.value
        else:
            raise ValueError(f"Key object does not contain raw value: {type(key)}")

        # Validate the key
        validate_symmetric_key(key_bytes, expected_algorithm="AES", expected_length=256)

        # Serialize and save the key
        write_serialized_symmetric_key(key_bytes, "symmetric_key.pem")

        print("Symmetric key successfully processed.")
    except Exception as e:
        print(f"Error handling symmetric key: {e}")
```

---

### **Example Output for Serialized Symmetric Key**

The file `symmetric_key.pem` will look like:
```plaintext
-----BEGIN AES KEY-----
U2FsdGVkX19GJzslLbNFwZkd02Tb8zRt3KcvVZ6FqI8=
-----END AES KEY-----
```

---

### **Advantages of This Approach**
1. **Interoperability**:
   - Base64-encoded PEM-like format is compatible with many systems and tools.
2. **Validation**:
   - Ensures the key meets your cryptographic expectations (e.g., algorithm and length).
3. **Ease of Use**:
   - Can be re-imported into the script for cryptographic operations.

Let me know if you need help integrating this approach into your KMIP workflow!