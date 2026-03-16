pipeline {
    agent {
        node {
            label 'docker'
        }
    }

    parameters {
        string(name: 'TARGET_REPO', defaultValue: 'BarkinKctp/ghapp-oidc-deploy-test', description: 'Repository cloned by container (owner/repo)')
        string(name: 'DOCKER_TEST_IMAGE', defaultValue: 'brkndocker/ghapp-test:latest', description: 'Docker image used by app/tests/docker_test.py')
        string(name: 'GH_TOKEN', defaultValue: 'gh-token', description: 'Secret text credential ID containing GH token')
        string(name: 'DOCKERHUB_CREDENTIALS_ID', defaultValue: 'dockerhub-creds', description: 'Username/Password credential ID for Docker Hub')
    }

    options {
        timestamps()
    }

    environment {
        PYTHONUNBUFFERED = '1'
        PIP_DISABLE_PIP_VERSION_CHECK = '1'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Publish GH App Test Image') {
            steps {
                withCredentials([
                    string(credentialsId: params.GH_TOKEN, variable: 'GH_TOKEN'),
                    usernamePassword(
                        credentialsId: params.DOCKERHUB_CREDENTIALS_ID,
                        usernameVariable: 'DOCKERHUB_USERNAME',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    script {
                        if (isUnix()) {
                            sh '''
                                set -e
                                echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin
                                python -m pip install --upgrade pip
                                pip install -r requirements.txt
                                export PYTHONPATH="$WORKSPACE"
                                export DOCKER_TEST_IMAGE="$DOCKER_TEST_IMAGE"
                                python -m app.build_dockerhub_packages
                            '''
                        } else {
                            powershell '''
                                $ErrorActionPreference = "Stop"
                                $env:DOCKERHUB_TOKEN | docker login -u $env:DOCKERHUB_USERNAME --password-stdin
                                python -m pip install --upgrade pip
                                pip install -r requirements.txt
                                $env:PYTHONPATH = $env:WORKSPACE
                                $env:DOCKER_TEST_IMAGE = "$env:DOCKER_TEST_IMAGE"
                                python -m app.build_dockerhub_packages
                            '''
                        }
                    }
                }
            }
        }

        stage('Test GH App Docker Flow') {
            steps {
                withCredentials([
                    string(credentialsId: params.GH_TOKEN, variable: 'GH_TOKEN'),
                    usernamePassword(
                        credentialsId: params.DOCKERHUB_CREDENTIALS_ID,
                        usernameVariable: 'DOCKERHUB_USERNAME',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    script {
                        if (isUnix()) {
                            sh '''
                                set -e
                                echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin
                                python -m pip install --upgrade pip
                                pip install -r requirements.txt
                                export PYTHONPATH="$WORKSPACE"
                                export TARGET_REPO="$TARGET_REPO"
                                export DOCKER_TEST_IMAGE="$DOCKER_TEST_IMAGE"
                                pytest -q app/tests/docker_test.py -s
                            '''
                        } else {
                            powershell '''
                                $ErrorActionPreference = "Stop"
                                $env:DOCKERHUB_TOKEN | docker login -u $env:DOCKERHUB_USERNAME --password-stdin
                                python -m pip install --upgrade pip
                                pip install -r requirements.txt
                                $env:PYTHONPATH = $env:WORKSPACE
                                $env:TARGET_REPO = "$env:TARGET_REPO"
                                $env:DOCKER_TEST_IMAGE = "$env:DOCKER_TEST_IMAGE"
                                pytest -q app/tests/docker_test.py -s
                            '''
                        }
                    }
                }
            }
        }
    }
}