import boto3

def create_vpc(config):
    ec2_client = boto3.client('ec2')
    try:
        vpc_response = ec2_client.create_vpc(CidrBlock=config['cidr_block'])
        vpc = vpc_response['Vpc']
        ec2_client.modify_vpc_attribute(VpcId=vpc['VpcId'], EnableDnsSupport={'Value': True})
        ec2_client.modify_vpc_attribute(VpcId=vpc['VpcId'], EnableDnsHostnames={'Value': True})
        print(f"Nandita's VPC Created with ID: {vpc['VpcId']}, DNS support and hostnames enabled.")
        return vpc
    except Exception as error:
        print(f"Failed to create VPC. Error: {error}")

