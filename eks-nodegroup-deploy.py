import boto3
import time
import argparse

def deploy_nodegroup(stack_name, cluster_name, region, subnet_ids, instance_types):

    cfn = boto3.client('cloudformation', region_name=region)

    # Load your template
    with open('eks-nodegroup-creation.yaml', 'r') as f:
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
                print(f"{stack_name} NodeGroup is being created...", end="\r")
                sys.stdout.flush()
                time.sleep(30)

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--stack_name', required=True)
    parser.add_argument('--cluster_name', required=True)
    parser.add_argument('--region', required=True)
    parser.add_argument('--subnet-ids', required=True)
    parser.add_argument('--instance_types', required=True)

    args = parser.parse_args()
    deploy_nodegroup(
        stack_name=args.stack_name,
        cluster_name=args.cluster_name,
        region=args.region,
        subnet_ids=args.subnet_ids,
        instance_types=args.instance_types
    )