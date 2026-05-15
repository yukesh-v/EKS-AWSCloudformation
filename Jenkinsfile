pipeline {
   
   agent any

parameters {
    string(name: 'CLUSTER_NAME', description: 'Name of the CloudFormation stack to create')
    string(name: 'REGION', defaultValue: 'ap-south-1', description: 'AWS region to deploy the stack')
    string(name: 'CLUSTER_VERSION', defaultValue: '1.35', description: 'Enter The Cluster Version')
    string(name: 'SUBNET_IDS', defaultValue: 'subnet-0b6d911bc173f3c89,subnet-0b3f113e6e4206a30', description: 'Comma-separated list of subnet IDs for the node group')
    string(name: 'SECURITY_GROUP', description: 'Security Group ID for the EKS cluster')
    string(name: 'INSTANCE_TYPES', defaultValue: 'c6a.large', description: 'Instance types for the node group')

}

stages {
    stage('Git Checkout'){
        steps {
            git branch: 'main', url: 'https://github.com/yukesh-v/EKS-AWSCloudformation.git'
        }
    }
    stage('Deploy EKS Cluster') {
        steps {
            script{
                sh 'python3 eks-cluster-creation.py --action cluster --stack_name ${CLUSTER_NAME} --region ${REGION} --subnet-ids ${SUBNET_IDS} --security-group ${SECURITY_GROUP} --cluster_version ${CLUSTER_VERSION} --instance_types ${INSTANCE_TYPES} --cluster_name ${CLUSTER_NAME}'
            }
        }
    }
    stage('Deploy EKS Node Group') {
        steps{
            script{
                sh 'python3 eks-cluster-creation.py --action nodes --stack_name ${CLUSTER_NAME} --region ${REGION} --subnet-ids ${SUBNET_IDS} --security-group ${SECURITY_GROUP} --cluster_version ${CLUSTER_VERSION} --instance_types ${INSTANCE_TYPES} --cluster_name ${CLUSTER_NAME}'
            }
        }
    }
    stage('Attach EKS Addons') {
        steps{
            script{
                sh 'python3 eks-cluster-creation.py --action addons --stack_name ${CLUSTER_NAME} --region ${REGION} --subnet-ids ${SUBNET_IDS} --security-group ${SECURITY_GROUP} --cluster_version ${CLUSTER_VERSION} --instance_types ${INSTANCE_TYPES} --cluster_name ${CLUSTER_NAME}'
            }
        }
    }
 }
 post {
        always {
            cleanWs()
        }
        success {
            echo 'EKS Cluster and Node Group Created successfully!'
        }
        failure {
                echo 'Deployment failed. Please check the logs for details.'
            }
    }
}