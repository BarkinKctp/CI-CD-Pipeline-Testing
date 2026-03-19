pipeline {
    agent {
        docker {
            image 'brkndocker/jenkins-agent:latest'
            args '-v /var/run/docker.sock:/var/run/docker.sock'
            label 'docker'
            registryUrl 'https://index.docker.io/v1/'
            registryCredentialsId 'jenkins-docker-login'
        }
    }

    parameters {
        string(name: 'TARGET_REPO', defaultValue: 'BarkinKctp/ghapp-oidc-deploy-test', description: 'Repository cloned by container (owner/repo)')
        string(name: 'DOCKER_TEST_IMAGE', defaultValue: 'brkndocker/ghapp-test:latest', description: 'Docker image used by app/tests/dockerhub_test.py')
        string(name: 'GH_CREDENTIALS_ID', defaultValue: 'ghapp-creds', description: 'Jenkins credential ID for your GitHub App (must be GitHub App type)')
}

    options {
        timestamps()
    }

    environment {
        PYTHONUNBUFFERED = '1'
        PIP_DISABLE_PIP_VERSION_CHECK = '1'
    }

    stages {
        stage("Checkout") {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: params.GH_CREDENTIALS_ID, // GitHub App credentials
                        usernameVariable: 'GITHUB_APP',
                        passwordVariable: 'GH_TOKEN'
                    )
                ]) {
                    script { env.GH_TOKEN = GH_TOKEN }
                    sh 'git config --global url."https://x-access-token:${GH_TOKEN}@github.com/".insteadOf "https://github.com/"'
                    checkout scm
                }
            }
        }
        stage("Setup") {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'jenkins-docker-login', // Docker Hub credentials
                        usernameVariable: 'DOCKERHUB_USERNAME',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                    set -e
                    echo $DOCKERHUB_TOKEN | docker login -u $DOCKERHUB_USERNAME --password-stdin
                    python3 -m pip install -r requirements.txt --break-system-packages 
                    '''
                }
            }
        }
        stage("Build, Test, and Push Docker Image") {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: params.GH_CREDENTIALS_ID, // GitHub App credentials
                        usernameVariable: 'GITHUB_APP',
                        passwordVariable: 'GH_TOKEN'
                    )
                ]) {
                    script { env.GH_TOKEN = GH_TOKEN }
                    sh '''
                    set -e
                    export PYTHONPATH="$WORKSPACE"
                    export TARGET_REPO="$TARGET_REPO"
                    export DOCKER_TEST_IMAGE="$DOCKER_TEST_IMAGE"
                    export GH_TOKEN="$GH_TOKEN"
                    curl -s -H "Authorization: token $GH_TOKEN" \
                        https://api.github.com/repos/BarkinKctp/ghapp-oidc-deploy-test \
                        | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('full_name', d.get('message', 'unknown')))"
                    python3 -m pytest -v app/tests/dockerhub_test.py
                    '''
                }
            }
        }
    }
}