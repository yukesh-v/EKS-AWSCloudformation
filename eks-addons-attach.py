import boto3
import time
import argparse
import sys

def attach_addons(stack_name, region, cluster_name):

    cfn = boto3.client('cloudformation', region_name=region)

    with open('eks-cluster-addon.yaml', 'r') as f:
        template_body = f.read()
    
    stack_name=f"{stack_name}-addons"

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
                print(f"{stack_name} Addons is being attaching to {cluster_name}...", end="\r", flush=True)
                sys.stdout.flush()
                time.sleep(30)

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--stack_name', required=True)
    parser.add_argument('--cluster_name', required=True)
    parser.add_argument('--region', required=True)

    args = parser.parse_args()
    attach_addons(
        stack_name=args.stack_name,
        cluster_name=args.cluster_name,
        region=args.region
    )