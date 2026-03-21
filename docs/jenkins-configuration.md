# Jenkins Configuration Guide

---

## 1. Prerequisites

- Docker Desktop installed and running on your machine
- A Docker Hub account (if pushing/pulling private images)
- (Optional) A GitHub App configured for webhook-based builds

---

## 2. Build the Custom Jenkins Image

Build the Jenkins image from the provided Dockerfile:

```powershell

cd docker/jenkins-image

docker build -t myjenkins:latest .
```

This image includes:

- Jenkins LTS with JDK 21
- Python 3 (via `python3-pip`)
- Docker CLI (to run Docker commands inside Jenkins)
- Essential pipeline and Docker plugins

---

## 3. Create the Docker Network

```powershell
docker network create jenkins
```

---

## 4. Run the Docker-in-Docker (DinD) Container

This container allows Jenkins to build and run Docker images:

```powershell
docker run --name docker --privileged --network jenkins `
  --env DOCKER_TLS_CERTDIR=/certs `
  --volume jenkins-docker-certs:/certs/client `
  --volume jenkins-data:/var/jenkins_home `
  -d docker:dind
```

---

## 5. Run the Jenkins Container

```powershell
docker run --name jenkins --restart=on-failure --detach `
  --network jenkins `
  --env DOCKER_HOST=tcp://docker:2376 `
  --volume jenkins-data:/var/jenkins_home `
  --publish 8080:8080 `
  --publish 50000:50000 `
  myjenkins:latest
```

Access Jenkins at: **http://localhost:8080**

---

## 6. Verify Docker Connectivity from Jenkins

Run this to confirm Jenkins can talk to the DinD container over TLS:

```powershell
docker exec jenkins sh -c "curl -s --cacert /certs/ca.pem --cert /certs/cert.pem --key /certs/key.pem https://docker:2376/version"
```

---

## 7. Configure Docker Cloud in Jenkins

1. Go to **Manage Jenkins → Clouds → New Cloud → Docker**
2. Set **Docker Host URI**: `tcp://docker:2376`
3. Set **Server credentials** to the TLS credentials (see step below)

### Export TLS Certificates (for Jenkins Docker Cloud credentials)

```powershell
docker run --rm `
  -v jenkins-docker-certs:/certs `
  -v "C:\Users\barki\Desktop:/output" `
  alpine sh -c "cp /certs/cert.pem /output/ && cp /certs/key.pem /output/ && cp /certs/ca.pem /output/"
```

Then in Jenkins, create an **X.509 Client Certificate** credential with all three files:

1. Go to **Manage Jenkins → Credentials → Add Credentials**
2. Kind: **X.509 Client Certificate**
3. ID: `docker-tls-certs`
4. Upload the three certificate files:
   - **Client Key File**: `key.pem`
   - **Client Certificate File**: `cert.pem`
   - **CA Certificate File**: `ca.pem`
5. Click **Create**

> **Important:** Jenkins requires **all three files** (`key.pem`, `cert.pem`, and `ca.pem`) to establish a secure connection to the DinD container. The certificate type must be **X.509 Client Certificate**.

Then in the Docker Cloud config reference this credential ID.

### Configure Docker Cloud

1. Go to **Manage Jenkins → Clouds → New Cloud → Docker**
2. Set **Docker Host URI**: `tcp://docker:2376`
3. Set **Server credentials**: Select the `docker-tls-certs` credential you just created
4. Click **Test Connection** to verify it works
5. Click **Save**

### Configure a Docker Cloud Agent Template

After setting up the Docker Cloud connection, you need an **agent template** so Jenkins can spin up containers to run builds.

> This project includes a custom agent image with Python and related tooling for running commands such as `pytest`.
>
> The image is **public on Docker Hub** and can be pulled directly:
>
> ```powershell
> docker pull brkndocker/jenkins-agent:latest
> ```
>
> Alternatively, you can build and push your own copy of the image.

1. Inside the Docker Cloud config, click **Docker Agent templates → Add Docker Template**
2. Configure the following:
   - **Labels**: `docker-agent`
   - **Enabled**: Checked
   - **Docker Image**: `brkndocker/jenkins-agent:latest`
   - **Remote File System Root**: `/home/jenkins/agent`
   - **Connect method**: **Attach Docker container**
   - **Pull strategy**: **Pull once and update latest**
3. Click **Save**

### Use Custom Agent Image (Optional)

If you prefer to build and push your own copy of the agent image, run:

```powershell
# Login to Docker Hub first
docker login

cd docker/jenkins-agent-image

docker build -t <yourdockerhubname>/jenkins-agent:latest .
docker push <yourdockerhubname>/jenkins-agent:latest
```

Then update the agent template **Docker Image** to: `<yourdockerhubname>/jenkins-agent:latest`

---

## 8. Configure Credentials in Jenkins

### Docker Hub Credentials (for private registries)

1. Go to **Manage Jenkins → Credentials → Add Credentials**
2. Kind: **Username with password**
3. ID: `jenkins-docker-login`
4. Username: Docker Hub username
5. Password: Docker Hub access token

> **Note:** The Jenkinsfile references `jenkins-docker-login` as the credential ID. The Jenkinsfile is hardcoded to use `jenkins-docker-login` as the credential ID, so you must name it exactly that and fill it with your Docker Hub credentials to be able to push or pull private images.

### GitHub App Credentials (optional, for GitHub App integration)

1. Go to **Manage Jenkins → Credentials → Add Credentials**
2. Kind: **GitHub App**
3. ID: `ghapp-creds`
4. Fill in: **App ID**, **Private Key**, and **Installation ID**

> **Important:** Jenkins requires the private key in **PKCS#8 format**. Convert it if needed:
>
> ```powershell
> openssl pkcs8 -topk8 -inform PEM -outform PEM -nocrypt -in <your-key>.pem -out new.pem
> ```

### Using GitHub App Credentials in a Jenkinsfile

```groovy
withCredentials([
    usernamePassword(
        credentialsId: params.GH_CREDENTIALS_ID,
        usernameVariable: 'GITHUB_APP',
        passwordVariable: 'GH_TOKEN'
    )
]) {
    // Your steps that require GitHub App authentication
}
```

---

## Quick Start Commands

```powershell
# 1. Build the Jenkins controller image
cd docker/jenkins-image
docker build -t myjenkins:latest .

# 2. Create the Docker network
docker network create jenkins

# 3. Start DinD
docker run --name docker --privileged --network jenkins `
  --env DOCKER_TLS_CERTDIR=/certs `
  --volume jenkins-docker-certs:/certs/client `
  --volume jenkins-data:/var/jenkins_home `
  -d docker:dind

# 4. Start Jenkins
docker run --name jenkins --restart=on-failure --detach `
  --network jenkins `
  --env DOCKER_HOST=tcp://docker:2376 `
  --volume jenkins-data:/var/jenkins_home `
  --publish 8080:8080 `
  --publish 50000:50000 `
  myjenkins:latest

# 5. Optional: pull the published agent image
docker pull brkndocker/jenkins-agent:latest

# 6. Get initial admin password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

---

## Troubleshooting

### Docker Cloud connection failed

- Verify DinD container is running:
  ```powershell
  docker ps --filter name=docker
  ```
- Check both containers are on the same network:

  ```powershell
  docker network inspect jenkins
  ```

- Ensure **X.509 Client Certificate** credential has all three files.
- Re-run the connectivity check from [Step 6](#6-verify-docker-connectivity-from-jenkins).

### "Permission denied" when running Docker commands inside Jenkins

- Ensure Jenkins is connecting to DinD with the correct TLS credentials.
- Confirm the `DOCKER_HOST` environment variable is set:

  ```powershell
  docker exec jenkins env | findstr DOCKER_HOST
  ```

- Should return: `DOCKER_HOST=tcp://docker:2376`

### Agent containers fail to start

- Verify agent image is accessible:
  ```powershell
  docker exec docker docker pull brkndocker/jenkins-agent:latest
  ```
- Check Jenkins logs:
  ```powershell
  docker logs jenkins --tail 50
  ```

### Cannot pull agent image from Docker Hub

- If using custom image, log in and push first:
  ```powershell
  docker login
  cd docker/jenkins-agent-image
  docker build -t <yourdockerhubname>/jenkins-agent:latest .
  docker push <yourdockerhubname>/jenkins-agent:latest
  ```

### Port 8080 already in use

**Symptom:** `Bind for 0.0.0.0:8080 failed: port is already allocated`

- Stop whatever is using port 8080, or map Jenkins to a different port:

  ```powershell
  docker run --name jenkins --restart=on-failure --detach `
    --network jenkins `
    --env DOCKER_HOST=tcp://docker:2376 `
    --volume jenkins-data:/var/jenkins_home `
    --publish 9090:8080 `
    --publish 50000:50000 `
    myjenkins:latest
  ```

- Then access Jenkins at **http://localhost:9090**.

### Forgot the initial admin password

```powershell
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### Need to start fresh

Remove all containers and volumes to reset everything:

```powershell
docker stop jenkins docker
docker rm jenkins docker
docker volume rm jenkins-data jenkins-docker-certs
docker network rm jenkins
```

Then re-run from [Step 2](#2-build-the-custom-jenkins-image).
