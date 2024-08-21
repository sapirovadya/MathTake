// pipeline { 
//     agent none
//     stages {
//         stage('Checkout') {
//             agent any
//             steps {
//                 checkout([
//                     $class: 'GitSCM',
//                     branches: [[name: '*/master']],
//                     userRemoteConfigs: [[
//                         url: 'https://github.com/BS-PMC-2024/BS-PMC-2024-Team16.git',
//                         credentialsId: 'jenkins_token1'
//                     ]]
//                 ])
//             }
//         }
//         stage('Build') {
//             agent {
//                 docker {
//                     image 'python:3.10-alpine'
//                     args '-u root:root'
//                 }
//             }
//             steps {
//                 sh 'pip install -r requirements.txt'
//             }
//         }
//         stage('Test') {
//             agent {
//                 docker {
//                     image 'python:3.10-alpine'
//                     args '-u root:root'
//                 }
//             }
//             steps {
//                 sh 'pip install -r requirements.txt'
//                 sh 'mkdir -p test-reports'
//                 sh 'pytest --junitxml=test-reports/results.xml --cov=. --cov-report=html'
//             }
//             post {
//                 always {
//                     junit 'test-reports/results.xml'
//                     archiveArtifacts artifacts: 'htmlcov/**', allowEmptyArchive: true
//                 }
//             }
//         }
//     }
// }


pipeline { 
    agent none
    stages {
        stage('Checkout') {
            agent any
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/master']],
                    userRemoteConfigs: [[
                        url: 'https://github.com/BS-PMC-2024/BS-PMC-2024-Team16.git',
                        credentialsId: 'jenkins_token1'
                    ]]
                ])
            }
        }
        stage('Build') {
            agent {
                docker {
                    image 'python:3.10-alpine'
                    args '-u root:root'
                }
            }
            steps {
                script {
                    def startTime = System.currentTimeMillis() // התחלת מדידת זמן ה-build
                    sh 'pip install -r requirements.txt'
                    def endTime = System.currentTimeMillis() // סיום מדידת זמן ה-build
                    def buildTime = (endTime - startTime) / 1000 // חישוב זמן ה-build בשניות
                    echo "Build time: ${buildTime} seconds"
                }
            }
        }
        stage('Test') {
            agent {
                docker {
                    image 'python:3.10-alpine'
                    args '-u root:root'
                }
            }
            steps {
                sh 'pip install -r requirements.txt'
                sh 'mkdir -p test-reports'
                sh 'pytest --junitxml=test-reports/results.xml --cov=. --cov-report=html'
            }
            post {
                always {
                    junit 'test-reports/results.xml'
                    archiveArtifacts artifacts: 'htmlcov/**', allowEmptyArchive: true
                }
            }
        }
        stage('Code Coverage') {
            agent any
            steps {
                echo 'Checking code coverage...'
                script {
                    def coverage = sh(script: "grep 'TOTAL' htmlcov/index.html | grep -oP '\\d+%' | head -1", returnStdout: true).trim()
                    echo "Code coverage is: ${coverage}"
                }
            }
        }
        stage('Build Success/Failure') {
            agent any
            steps {
                script {
                    def successfulBuilds = currentBuild.result == 'SUCCESS' ? 1 : 0
                    def failedBuilds = currentBuild.result == 'FAILURE' ? 1 : 0
                    echo "Number of successful builds: ${successfulBuilds}"
                    echo "Number of failed builds: ${failedBuilds}"
                }
            }
        }
        stage('Test Success/Failure') {
            agent any
            steps {
                script {
                    def testResults = sh(script: "grep '<testsuite' test-reports/results.xml | grep -oP 'tests=\"\\d+\"' | grep -oP '\\d+'", returnStdout: true).trim()
                    def failedTests = sh(script: "grep '<testsuite' test-reports/results.xml | grep -oP 'failures=\"\\d+\"' | grep -oP '\\d+'", returnStdout: true).trim()
                    def passedTests = Integer.parseInt(testResults) - Integer.parseInt(failedTests)
                    echo "Number of passed tests: ${passedTests}"
                    echo "Number of failed tests: ${failedTests}"
                }
            }
        }
    }
}
