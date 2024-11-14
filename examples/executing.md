# Running `rotate_kmip_key` in Native Python, Executable, and Docker

This guide provides examples for running the `rotate_kmip_key` program in three different environments: native Python, Windows executable, and Docker. Each example assumes the `config.ini` file is configured and contains the necessary settings.

## 1. Running in Native Python

```bash
python rotate_kmip_key.py --config config.ini
```

### Requirements
- Python 3.8+ installed on your system.
- Dependencies from `requirements.txt` are installed:
  ```bash
  pip install -r requirements.txt
  ```
- Ensure `config.ini` is in the same directory as the script, or specify its full path if it’s located elsewhere.

## 2. Running the Windows Executable

```bash
rotate_kmip_key.exe --config config.ini
```

### Requirements
- The `rotate_kmip_key.exe` file should be in the same directory as `config.ini`, or provide the full path to `config.ini` when running the command.
- No additional dependencies are required, as the executable includes all necessary libraries.

## 3. Running in Docker

```bash
docker run --rm -v /path/to/config:/app/config -v /path/to/output:/app/output my-kmip-client --config /app/config/config.ini
```

### Requirements
- **Volumes**:
  - Replace `/path/to/config` with the full path on your host machine to the folder containing `config.ini`.
  - Replace `/path/to/output` with the path on your host machine where you want output files to be saved.
- **Docker Image**:
  - `my-kmip-client` should be the name of your Docker image. Ensure it’s already built or available from a container registry if not locally available.
```