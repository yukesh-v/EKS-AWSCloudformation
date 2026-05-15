import boto3
import time
import argparse

def attach_addons(stack_name, region,):

    parser = argparse.ArgumentParser()
    parser.add_argument('--stack-name', required=True)
    parser.add_argument('--region', required=True)


    cfn = boto3.client('cloudformation', region_name=region)

    # Load your template
    with open('eks-cluster-addon.yaml', 'r') as f:
        template_body = f.read()
    
    stack_name = stack_name

    print(f"Starting deployment for node group {stack_name}...")

    try:
        response = cfn.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=[
                {'ParameterKey': 'ClusterName', 'ParameterValue': stack_name}
            ],
            Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
        )
        
        print("Stack creation initiated. ID:", response['StackId'])

        waiter = cfn.get_waiter('stack_create_complete')
        print(f"Waiting for EKS Addons to attach to {stack_name}...")
        waiter.wait(StackName=stack_name)
        print("Addons Complete!")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":

    args = parser.parse_args()
    attach_addons(
        stack_name=args.stack_name,
        region=args.region
    )