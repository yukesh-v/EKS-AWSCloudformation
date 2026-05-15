import boto3
import time
import argparse

def deploy_cluster(stack_name, region, subnet_ids, vpc_id, cluster_version, security_group):
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--stack-name', required=True)
    parser.add_argument('--region', required=True)
    parser.add_argument('--subnet-ids', required=True)
    parser.add_argument('--vpc-id', required=True)
    parser.add_argument('--security-group', required=True)
    parser.add_argument('--cluster-version', default="1.35")

    cfn = boto3.client('cloudformation', region_name=region)
    # Load your template
    with open('eks-cluster-create.yaml', 'r') as f:
        template_body = f.read()
    
    stack_name = stack_name

    print(f"Starting deployment for {stack_name}...")

    try:
        response = cfn.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=[
                {'ParameterKey': 'ClusterName', 'ParameterValue': stack_name},
                {'ParameterKey': 'VpcId', 'ParameterValue': vpc_id},
                {'ParameterKey': 'SubnetIds', 'ParameterValue': ','.join(subnet_ids)},
                {'ParameterKey': 'ClusterVersion', 'ParameterValue': cluster_version},
                {'ParameterKey': 'SecurityGroup', 'ParameterValue': security_group}
            ],
            Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
        )
        
        print("Stack creation initiated. ID:", response['StackId'])
        
        # Wait for completion (EKS takes ~15-20 minutes)
        waiter = cfn.get_waiter('stack_create_complete')
        print("Waiting for EKS cluster and nodes to provision...")
        waiter.wait(StackName=stack_name)
        print("Deployment Complete!")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":

args = parser.parse_args()
    deploy_cluster(
        stack_name=args.stack_name,
        region=args.region,
        subnet_ids=args.subnet_ids,
        vpc_id=args.vpc_id,
        cluster_version=args.cluster_version,
        security_group=args.security_group
    )