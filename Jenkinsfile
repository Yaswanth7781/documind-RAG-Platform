pipeline {
    agent any

    environment {
        DOCKER_COMPOSE_FILE = 'docker-compose.yml'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Services') {
            steps {
                echo 'Building Docker images for all microservices...'
                sh "docker-compose -f ${DOCKER_COMPOSE_FILE} build"
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'
                echo 'Skipping tests for now...'
            }
        }

        stage('Create Environment File') {
            steps {
                withCredentials([
                    string(credentialsId: 'groq-api-key', variable: 'GROQ_API_KEY'),
                    string(credentialsId: 'pinecone-api-key', variable: 'PINECONE_API_KEY'),
                    string(credentialsId: 'admin-pin', variable: 'ADMIN_PIN')
                ]) {
                    sh '''
                    cat > .env << EOF
GROQ_API_KEY=$GROQ_API_KEY
GROQ_MODEL=llama-3.1-8b-instant
GROQ_BASE_URL=https://api.groq.com/openai/v1/chat/completions

PINECONE_API_KEY=$PINECONE_API_KEY
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=documind-index-1024

ADMIN_PIN=$ADMIN_PIN
EOF

                    echo "Created .env file"
                    ls -la .env
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying application...'

                sh """
                docker-compose -f ${DOCKER_COMPOSE_FILE} down || true
                docker-compose -f ${DOCKER_COMPOSE_FILE} up -d
                """
            }
        }

        stage('Verify Deployment') {
            steps {
                sh 'docker ps'
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution finished.'
        }

        success {
            echo 'Pipeline succeeded successfully!'
        }

        failure {
            echo 'Pipeline failed. Please check the logs.'
        }
    }
}