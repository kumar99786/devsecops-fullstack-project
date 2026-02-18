pipeline {
    agent { label 'docker-agent' }


    options {
        buildDiscarder(logRotator(
            numToKeepStr: '5',
            artifactNumToKeepStr: '5'
        ))
        timestamps()
    }

    environment {
        IMAGE_NAME = "devsecops-app"
        IMAGE_TAG  = "${BUILD_NUMBER}"

        DB_HOST = "localhost"
        DB_USER = "testuser"
        DB_NAME = "testdb"
        DB_PASSWORD = credentials('mysql-password-id')
    }

    stages {
        stage('DEBUG VERSION') {
    steps {
        echo "PIPELINE VERSION 3.0"
    }
}

        stage('Clean Workspace') {
        steps {
            deleteDir()
        }
    }

    stage('Checkout') {
        steps {
            checkout scm
        }
    }

        stage('Install Dependencies') {
    steps {
        dir('backend') {
            sh '''
                rm -rf venv
                python3 -m venv venv
                venv/bin/pip install -r requirements.txt
                venv/bin/pip install -r requirements-dev.txt
            '''
        }
    }
}

stage('Run Unit Tests & Coverage') {
    steps {
        sh '''
            PYTHONPATH=. backend/venv/bin/pytest backend/tests \
              --cov=backend \
              --cov-report=xml:backend/coverage.xml
        '''
    }
}

        stage('SonarQube Analysis') {
    steps {
        script {
            def scannerHome = tool 'SonarScanner'
            withSonarQubeEnv('SonarQube') {
                withEnv(["PATH+SONAR=${scannerHome}/bin"]) {
                    sh '''
                        sonar-scanner \
                          -Dsonar.projectKey=devsecops-fullstack-project \
                          -Dsonar.sources=backend \
                          -Dsonar.python.coverage.reportPaths=backend/coverage.xml
                    '''
                }
            }
        }
    }
}

stage('Quality Gate') {
    steps {
        script {
            timeout(time: 5, unit: 'MINUTES') {
                waitForQualityGate abortPipeline: true
            }
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
                sh 'docker build -t $IMAGE_NAME:$IMAGE_TAG ./backend'
            }
        }

        stage('Trivy Image Scan') {
            steps {
                sh '''
                    trivy image \
                      --exit-code 1 \
                      --severity CRITICAL \
                      $IMAGE_NAME:$IMAGE_TAG
                '''
            }
        }
    }

    post {
        always {
            script {
                node {
                    sh 'docker system prune -af --volumes || true'
                }
            }
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
