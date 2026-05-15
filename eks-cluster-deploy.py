import boto3
import time
import argparse
import sys

def deploy_cluster(stack_name, region, subnet_ids, vpc_id, cluster_version, security_group):

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
                {'ParameterKey': 'SubnetIds', 'ParameterValue': subnet_ids},
                {'ParameterKey': 'ClusterVersion', 'ParameterValue': cluster_version},
                {'ParameterKey': 'SecurityGroup', 'ParameterValue': security_group}
            ],
            Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
        )
        
        print("Stack creation initiated. ID:", response['StackId'])
        
        while True:
            stack = cfn.describe_stacks(StackName=stack_name)['Stacks'][0]
            status = stack['StackStatus']
            
            if status == 'CREATE_COMPLETE':
                print("\nCluster is Created Complete!")
                break
            elif 'FAILED' in status or 'ROLLBACK' in status:
                print(f"\nDeployment Failed with status: {status}")
                break
            else:
                print(f"{stack_name} Cluster is being created...", end="\r")
                sys.stdout.flush()
                time.sleep(30)

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--stack_name', required=True)
    parser.add_argument('--region', required=True)
    parser.add_argument('--subnet-ids', required=True)
    parser.add_argument('--vpc-id', required=True)
    parser.add_argument('--security-group', required=True)
    parser.add_argument('--cluster_version', default="1.35")

    args = parser.parse_args()
    deploy_cluster(
        stack_name=args.stack_name,
        region=args.region,
        subnet_ids=args.subnet_ids,
        vpc_id=args.vpc_id,
        cluster_version=args.cluster_version,
        security_group=args.security_group
    )