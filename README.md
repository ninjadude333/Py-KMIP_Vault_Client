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