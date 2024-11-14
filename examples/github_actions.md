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