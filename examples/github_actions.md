To set up GitHub Actions to automatically build both a Docker image and a Windows executable file whenever a push is made, you can create a GitHub Actions workflow file in your repository. Here’s a guide on how to set up the workflow with both goals:

### Step 1: Define the Workflow in GitHub Actions
In your repository, create a `.github/workflows/build.yml` file to define the workflow.

### GitHub Actions Workflow File: `.github/workflows/build.yml`

```yaml
name: Build Docker Image and Windows Executable

on:
  push:
    branches:
      - main  # Trigger on push to main branch; adjust if necessary

jobs:
  build_docker:
    runs-on: ubuntu-latest
    steps:
      - name: Check out code
        uses: actions/checkout@v2

      - name: Log into Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build Docker image
        run: docker build -t my-kmip-client .

      - name: Push Docker image
        run: docker push my-kmip-client:latest

  build_windows_exe:
    runs-on: windows-latest
    steps:
      - name: Check out code
        uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pyinstaller configparser pymip

      - name: Build Windows executable
        run: pyinstaller --onefile rotate_kmip_key.py

      - name: Upload Windows executable artifact
        uses: actions/upload-artifact@v3
        with:
          name: kmip_client_windows_exe
          path: dist/rotate_kmip_key.exe
```

### Explanation of Workflow

1. **Trigger**: This workflow runs on every push to the `main` branch. You can adjust the branch name or add more triggers if needed.
2. **Docker Build Job**:
   - Runs on `ubuntu-latest`.
   - Logs into Docker Hub using GitHub Secrets for `DOCKER_USERNAME` and `DOCKER_PASSWORD`. Set these secrets in your repository’s settings.
   - Builds the Docker image with the `docker build` command and pushes it to Docker Hub.

3. **Windows Executable Build Job**:
   - Runs on `windows-latest`.
   - Sets up Python and installs dependencies.
   - Uses `pyinstaller` to package `rotate_kmip_key.py` into a single executable `.exe` file.
   - Uploads the built `.exe` as an artifact in GitHub Actions, which you can download from the Actions interface.

### Step 2: Configure Docker Hub Credentials in GitHub Secrets

1. Go to your repository’s **Settings** > **Secrets**.
2. Add `DOCKER_USERNAME` and `DOCKER_PASSWORD` as repository secrets with your Docker Hub credentials.

### Step 3: Run the Workflow

After setting up this workflow, each push to the main branch will trigger the build:
- The Docker image will be built and pushed to Docker Hub.
- The Windows executable file will be created and saved as an artifact in the GitHub Actions workflow for download.

### Optional: Download the Windows Executable Artifact

After a successful build, navigate to **Actions** in your GitHub repository, select the latest workflow run, and download the `kmip_client_windows_exe` artifact, which contains `rotate_kmip_key.exe`.

Yes, there are several ways to automate the login process to Docker Hub without exposing credentials directly. Here are a few options:

### 1. **Using Docker's `docker login` with Environment Variables**
You can automate the Docker login process by setting your Docker Hub credentials as environment variables. This way, you can avoid storing them directly in scripts or exposing them in plain text.

#### Steps:
- Set the environment variables for Docker Hub credentials:
  ```bash
  export DOCKER_USERNAME=<your_dockerhub_username>
  export DOCKER_PASSWORD=<your_dockerhub_password>
  ```

- Use these environment variables in a script to log in:
  ```bash
  echo $DOCKER_PASSWORD | docker login --username $DOCKER_USERNAME --password-stdin
  ```

# DOCKER HUB CREDS

This will log in to Docker Hub without having to hard-code your username and password.

### 2. **Using Docker's `docker login` with Docker Config File**
If you want to avoid storing credentials in environment variables, you can use the `docker login` command to store credentials securely in the `~/.docker/config.json` file.

#### Steps:
- First, manually run `docker login` (this will store your credentials securely in the config file):
  ```bash
  docker login
  ```

- Docker will prompt you for your username and password and will store them in the config file. This allows for automatic login on subsequent Docker commands.

### 3. **Using Docker Hub with GitHub Actions (or other CI/CD services)**
You can automate the Docker login within CI/CD pipelines using secrets, ensuring that your credentials are securely stored and never exposed in plain text.

#### Example for GitHub Actions:
1. **Store Docker Credentials in GitHub Secrets:**
   - Go to your GitHub repository, navigate to `Settings` > `Secrets`, and add `DOCKER_USERNAME` and `DOCKER_PASSWORD` as secrets.

2. **Use the secrets in your GitHub Actions workflow:**
   ```yaml
   name: Build and Push Docker Image

   on:
     push:
       branches:
         - main

   jobs:
     build:
       runs-on: ubuntu-latest

       steps:
         - name: Check out code
           uses: actions/checkout@v2

         - name: Log in to Docker Hub
           uses: docker/login-action@v2
           with:
             username: ${{ secrets.DOCKER_USERNAME }}
             password: ${{ secrets.DOCKER_PASSWORD }}

         - name: Build and push Docker image
           run: |
             docker build -t my-image .
             docker push my-image
   ```

This way, your Docker Hub credentials are safely stored in GitHub Secrets and are automatically injected into your CI/CD pipeline.

### 4. **Using AWS Secrets Manager / Azure Key Vault / Google Cloud Secret Manager**
For more advanced scenarios, especially in cloud environments, you can store your credentials in a secret management system (like AWS Secrets Manager, Azure Key Vault, or Google Cloud Secret Manager) and retrieve them programmatically during your CI/CD pipeline execution.

- **AWS Example** (Using AWS CLI):
  ```bash
  export DOCKER_USERNAME=$(aws secretsmanager get-secret-value --secret-id dockerhub/username --query SecretString --output text)
  export DOCKER_PASSWORD=$(aws secretsmanager get-secret-value --secret-id dockerhub/password --query SecretString --output text)
  
  echo $DOCKER_PASSWORD | docker login --username $DOCKER_USERNAME --password-stdin
  ```

This approach provides a secure way to manage secrets and integrates well with cloud-native CI/CD workflows.

### 5. **Using Docker's Credential Helpers**
Docker supports credential helpers that store credentials securely in a system-specific manner (e.g., in the macOS Keychain, Windows Credentials Store, or Linux-based helpers).

- Install Docker's credential helper:
  ```bash
  docker-credential-helper
  ```

- Configure Docker to use the credential helper by modifying the Docker configuration file (`~/.docker/config.json`):
  ```json
  {
    "credsStore": "osxkeychain"  // Example for macOS, change to appropriate store for your system
  }
  ```

This will store your Docker credentials securely and automatically log you in using the stored credentials.

### Conclusion
Each of these methods provides a secure way to log in to Docker Hub without exposing your credentials directly. For automated setups, using environment variables, CI/CD secrets, or Docker credential helpers are the most commonly recommended approaches.