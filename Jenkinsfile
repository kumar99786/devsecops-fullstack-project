pipeline {
    agent { label 'docker-agent' }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
    }

    environment {
        AWS_REGION = "us-east-1"
        ECR_REPO   = "957117875403.dkr.ecr.us-east-1.amazonaws.com/devsecops-app"
        IMAGE_TAG  = "${BUILD_NUMBER}"
        GITOPS_REPO = "https://github.com/kumar99786/devsecops-gitops-ms.git"
    }

    stages {

        stage('Clean Workspace') {
            steps { deleteDir() }
        }

        stage('Checkout Source Code') {
            steps { checkout scm }
        }

        stage('Install Dependencies') {
            steps {
                dir('backend') {
                    sh '''
                        python3 -m venv venv
                        venv/bin/pip install -r requirements.txt
                        venv/bin/pip install -r requirements-dev.txt
                    '''
                }
            }
        }

        stage('Run Unit Tests') {
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
                        sh """
                        ${scannerHome}/bin/sonar-scanner \
                        -Dsonar.projectKey=devsecops-fullstack-project \
                        -Dsonar.sources=backend \
                        -Dsonar.python.coverage.reportPaths=backend/coverage.xml
                        """
                    }
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
                    trivy fs --exit-code 1 --severity HIGH,CRITICAL .
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh """
                    docker build -t $ECR_REPO:$IMAGE_TAG ./backend
                """
            }
        }

        stage('Trivy Image Scan') {
            steps {
                sh '''
                    trivy image --exit-code 1 --severity CRITICAL $ECR_REPO:$IMAGE_TAG
                '''
            }
        }

        stage('Push Image to ECR') {
            steps {
                sh '''
                    aws ecr get-login-password --region $AWS_REGION | \
                    docker login --username AWS --password-stdin 957117875403.dkr.ecr.us-east-1.amazonaws.com

                    docker push $ECR_REPO:$IMAGE_TAG
                '''
            }
        }

        stage('Deploy to DEV (Auto GitOps)') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'gitops-creds', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
                    sh '''
                        git clone https://$GIT_USER:$GIT_TOKEN@github.com/kumar99786/devsecops-gitops-ms.git
                        cd devsecops-gitops-ms/environments
                        sed -i "s/tag:.*/tag: \\"$IMAGE_TAG\\"/" dev-values.yaml
                        git config user.email "jenkins@devsecops.com"
                        git config user.name "Jenkins"
                        git commit -am "Deploy to DEV - Tag $IMAGE_TAG"
                        git push
                    '''
                }
            }
        }

        stage('Approve QA Deployment') {
            steps {
                input message: "Deploy build $IMAGE_TAG to QA?"
            }
        }

        stage('Promote to QA') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'gitops-creds', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
                    sh '''
                        cd devsecops-gitops-ms/environments
                        sed -i "s/tag:.*/tag: \\"$IMAGE_TAG\\"/" qa-values.yaml
                        git commit -am "Promote to QA - Tag $IMAGE_TAG"
                        git push
                    '''
                }
            }
        }

        stage('Approve PROD Deployment') {
            steps {
                input message: "Deploy build $IMAGE_TAG to PROD?"
            }
        }

        stage('Promote to PROD') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'gitops-creds', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_TOKEN')]) {
                    sh '''
                        cd devsecops-gitops-ms/environments
                        sed -i "s/tag:.*/tag: \\"$IMAGE_TAG\\"/" prod-values.yaml
                        git commit -am "Promote to PROD - Tag $IMAGE_TAG"
                        git push
                    '''
                }
            }
        }
    }

    post {
        always {
            sh 'docker system prune -af || true'
        }
        success {
            echo "CI/CD pipeline completed successfully."
        }
        failure {
            echo "Pipeline failed."
        }
    }
}
