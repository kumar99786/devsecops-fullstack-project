pipeline {
    agent { label 'docker-agent' }

    stages {
        stage('Checkout') {
            steps {
                echo "Code pulled automatically from GitHub"
            }
        }

        stage('List Files') {
            steps {
                sh 'ls -la'
            }
        }
    }
}

