import boto3
import time
import argparse

def deploy_nodegroup(stack_name, region, subnet_ids, instance_types):

    parser = argparse.ArgumentParser()
    parser.add_argument('--stack-name', required=True)
    parser.add_argument('--region', required=True)
    parser.add_argument('--subnet-ids', required=True)
    parser.add_argument('--instance_types', required=True)

    cfn = boto3.client('cloudformation', region_name=region)

    # Load your template
    with open('eks-nodegroup-creation.yaml', 'r') as f:
        template_body = f.read()
    
    stack_name = stack_name

    print(f"Starting deployment for node group {stack_name}...")

    try:
        response = cfn.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=[
                {'ParameterKey': 'ClusterName', 'ParameterValue': stack_name},
                {'ParameterKey': 'SubnetIds', 'ParameterValue': ','.join(subnet_ids)},
                {'ParameterKey': 'InstanceTypes', 'ParameterValue': instance_types}
            ],
            Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
        )
        
        print("Stack creation initiated. ID:", response['StackId'])

        waiter = cfn.get_waiter('stack_create_complete')
        print("Waiting for EKS node group to provision...")
        waiter.wait(StackName=stack_name)
        print("Node Group Complete!")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":

    args = parser.parse_args()
    deploy_nodegroup(
        stack_name=args.stack_name,
        region=args.region,
        subnet_ids=args.subnet_ids,
        instance_types=args.instance_types
    )