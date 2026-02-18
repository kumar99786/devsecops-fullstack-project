pipeline {
    agent { label 'docker-agent' }

    environment {
        IMAGE_NAME = "devsecops-app"
        IMAGE_TAG = "${BUILD_NUMBER}"
        DB_PASSWORD = credentials('mysql-password-id')
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh '''
                    /opt/sonar-scanner/bin/sonar-scanner \
                    -Dsonar.projectKey=devsecops-project \
                    -Dsonar.sources=.
                    '''
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Trivy Filesystem Scan') {
            steps {
                sh '''
                trivy fs \
                  --exit-code 1 \
                  --severity HIGH,CRITICAL \
                  .
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                docker build -t $IMAGE_NAME:$IMAGE_TAG ./backend
                '''
            }
        }

        stage('Trivy Image Scan') {
            steps {
                sh '''
                trivy image \
                  --exit-code 1 \
                  --severity HIGH,CRITICAL \
                  $IMAGE_NAME:$IMAGE_TAG
                '''
            }
        }
    }
}
