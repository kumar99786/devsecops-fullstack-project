pipeline {
    agent { label 'docker-agent' }

    environment {
        IMAGE_NAME = "devsecops-app"
        IMAGE_TAG  = "${BUILD_NUMBER}"

        // Database env vars (safe for tests)
        DB_HOST = "localhost"
        DB_USER = "testuser"
        DB_NAME = "testdb"
        DB_PASSWORD = credentials('mysql-password-id')
    }

    options {
        timestamps()
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    cd backend
                    python3 -m pip install --upgrade pip
                    python3 -m pip install -r requirements.txt
                    python3 -m pip install -r requirements-dev.txt
                '''
            }
        }

        stage('Run Unit Tests & Generate Coverage') {
            steps {
                sh '''
                    cd backend
                    python3 -m pytest --cov=app --cov-report=xml
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh '''
                        cd backend
                        sonar-scanner \
                          -Dsonar.projectKey=devsecops-fullstack-project \
                          -Dsonar.sources=. \
                          -Dsonar.python.coverage.reportPaths=coverage.xml
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

    post {
        always {
            echo "Pipeline execution completed."
        }
        success {
            echo "Application passed all quality and security checks."
        }
        failure {
            echo "Pipeline failed. Check logs for details."
        }
    }
}
