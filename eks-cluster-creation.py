import boto3
import time
import argparse
import sys

def create_cluster(stack_name, region, subnet_ids, cluster_version, security_group):
    cfn = boto3.client('cloudformation', region_name=region)

    # Load your template
    with open('eks-control-node.yaml', 'r') as f:
        template_body = f.read()
    
    stack_name = stack_name

    try:
        response = cfn.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=[
                {'ParameterKey': 'ClusterName', 'ParameterValue': stack_name},
                {'ParameterKey': 'SubnetIds', 'ParameterValue': subnet_ids},
                {'ParameterKey': 'ClusterVersion', 'ParameterValue': cluster_version},
                {'ParameterKey': 'SecurityGroup', 'ParameterValue': security_group}
            ],
            Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
        )
        
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
                print(f"{stack_name} is being created...", end="\r", flush=True)
                sys.stdout.flush()
                time.sleep(30)

    except Exception as e:
        print(f"Error: {str(e)}")

def create_nodegroup(stack_name, region, subnet_ids, instance_types, cluster_name):
    cfn = boto3.client('cloudformation', region_name=region)

    # Load your template
    with open('eks-nodegroup.yaml', 'r') as f:
        template_body = f.read()
    
    stack_name = f"{stack_name}-nodegroup"

    print(f"Starting deployment for node group {stack_name}...")

    try:
        response = cfn.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=[
                {'ParameterKey': 'ClusterName', 'ParameterValue': cluster_name},
                {'ParameterKey': 'SubnetIds', 'ParameterValue': subnet_ids},
                {'ParameterKey': 'InstanceTypes', 'ParameterValue': instance_types}
            ],
            Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
        )
        
        while True:
            stack = cfn.describe_stacks(StackName=stack_name)['Stacks'][0]
            status = stack['StackStatus']
            
            if status == 'CREATE_COMPLETE':
                print("\nNodeGroup is Created !")
                break
            elif 'FAILED' in status or 'ROLLBACK' in status:
                print(f"\nNodeGroup Failed with status: {status}")
                break
            else:
                print(f"{stack_name} is being created...", end="\r", flush=True)
                sys.stdout.flush()
                time.sleep(30)

    except Exception as e:
        print(f"Error: {str(e)}")

def attach_addons(stack_name, region, cluster_name):
    cfn = boto3.client('cloudformation', region_name=region)

    # Load your template
    with open('eks-addons.yaml', 'r') as f:
        template_body = f.read()
    
    stack_name = f"{stack_name}-addon"

    try:
        response = cfn.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=[
                {'ParameterKey': 'ClusterName', 'ParameterValue': cluster_name}
            ],
            Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
        )

        while True:
            stack = cfn.describe_stacks(StackName=stack_name)['Stacks'][0]
            status = stack['StackStatus']
            
            if status == 'CREATE_COMPLETE':
                print("\nAddons is Attached !")
                break
            elif 'FAILED' in status or 'ROLLBACK' in status:
                print(f"\nAddons Failed with status: {status}")
                break
            else:
                print(f"{stack_name} is being attaching to {cluster_name}...", end="\r", flush=True)
                sys.stdout.flush()
                time.sleep(30)
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', required=True, choices=['cluster', 'nodes', 'addons'])

    parser.add_argument('--stack_name', required=True)
    parser.add_argument('--cluster_name', required=True)
    parser.add_argument('--region', required=True)
    parser.add_argument('--subnet-ids', required=True)
    parser.add_argument('--security-group', required=True)
    parser.add_argument('--cluster_version', default="1.35")
    parser.add_argument('--instance_types', required=True)

    args = parser.parse_args()

    if args.action == 'cluster':
        create_cluster(
            stack_name=args.stack_name,
            region=args.region,
            subnet_ids=args.subnet_ids,
            cluster_version=args.cluster_version,
            security_group=args.security_group
        )
    elif args.action == 'nodes':
        create_nodegroup(
            stack_name=args.stack_name,
            region=args.region,
            cluster_name=args.cluster_name,
            subnet_ids=args.subnet_ids,
            instance_types=args.instance_types
        )
    elif args.action == 'addons':
        attach_addons(
            stack_name=args.stack_name,
            region=args.region,
            cluster_name=args.cluster_name
        )

