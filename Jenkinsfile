pipeline {
    agent any

    environment {
        DOCKER_COMPOSE_FILE = 'docker-compose.yml'
    }

    stages {
        stage('Checkout') {
            steps {
                // Checkout code from the configured source control repository
                checkout scm
            }
        }

        stage('Build Services') {
            steps {
                echo 'Building Docker images for all microservices...'
                // Build all services defined in docker-compose.yml
                // Note: Change 'sh' to 'bat' if Jenkins is running on a Windows node without bash
                sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} build'
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'
                // Add your testing steps here. For example:
                // sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} run --rm api-gateway pytest'
                // sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} run --rm frontend npm test'
                echo 'Skipping tests for now...'
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                // Start the services in detached mode
                sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} up -d'
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution finished.'
            // Optional: clean up resources or bring down containers
            // sh 'docker-compose -f ${DOCKER_COMPOSE_FILE} down'
        }
        success {
            echo 'Pipeline succeeded successfully!'
        }
        failure {
            echo 'Pipeline failed. Please check the logs.'
        }
    }
}
