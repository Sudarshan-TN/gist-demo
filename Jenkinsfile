pipeline {

    agent { label 'windows' }

    options {
            timeout(time: 10, unit: 'MINUTES')
            disableConcurrentBuilds()
            buildDiscarder(logRotator(numToKeepStr: '5'))

        }

    triggers {
        pollSCM('* * * * *')
    }

    environment {
        IMAGE_NAME = "list-gists"
        // Actual project folder on Windows
//        PROJECT_DIR = "C:\\Users\\sudar\\PycharmProjects\\equal-experts-nonchalant-blissful-luminous-vision-40ed1ed446c5"

    }

    stages {
        stage('Initialize') {
            steps {
                script {
                    // Set a descriptive build name
                    currentBuild.displayName = "${IMAGE_NAME}:${IMAGE_TAG}-#${env.BUILD_NUMBER}"
                    echo "Running on host at: ${env.PROJECT_DIR}"
                    cleanWs()

                }
            }
        }

        stage('Git Checkout') {
            steps {
                script {
                    git branch: 'main', credentialsId: 'github-sud', url: 'https://github.com/Sudarshan-TN/gist-demo.git'
                }
            }
        }

        stage('Setup & Install') {
            steps {

                bat "uv --version"
                bat "uv sync --frozen"

            }
        }

        stage('Run Tests') {
            steps {

                script {
                    bat "uv run pytest -v --junitxml=results.xml"
                }
                // Archive test results
                junit 'results.xml'

            }
        }

        stage('Build Docker Image') {
            steps {
                    bat "docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} ."
            }
        }

        stage('Deploy') {
            steps {
                bat "docker run -d -p 8080:8080 --cap-drop=ALL --security-opt=no-new-privileges:true ${IMAGE_NAME}:${BUILD_NUMBER}"
            }
        }
    }

    post {
        success { echo "Pipeline completed successfully." }
        failure { echo "Pipeline failed. Check if the agent is connected and 'uv' is in PATH." }
    }
}