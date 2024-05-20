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


def delete_vpc(vpc_id):
    ec2_client = boto3.client('ec2')
    try:
        # Detach and delete all associated resources like internet gateways
        igws = ec2_client.describe_internet_gateways(Filters=[{'Name': 'attachment.vpc-id', 'Values': [vpc_id]}])
        for igw in igws['InternetGateways']:
            ec2_client.detach_internet_gateway(InternetGatewayId=igw['InternetGatewayId'], VpcId=vpc_id)
            ec2_client.delete_internet_gateway(InternetGatewayId=igw['InternetGatewayId'])
        
        # Delete subnets
        subnets = ec2_client.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
        for subnet in subnets['Subnets']:
            ec2_client.delete_subnet(SubnetId=subnet['SubnetId'])

        # Delete security groups
        sgs = ec2_client.describe_security_groups(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
        for sg in sgs['SecurityGroups']:
            if sg['GroupName'] != 'default':
                ec2_client.delete_security_group(GroupId=sg['GroupId'])

        # Delete route tables
        rts = ec2_client.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
        for rt in rts['RouteTables']:
            if not rt['Associations']:  # Avoid deleting the main route table
                ec2_client.delete_route_table(RouteTableId=rt['RouteTableId'])

        # Finally delete the VPC
        ec2_client.delete_vpc(VpcId=vpc_id)
        print(f"Deleted VPC with ID: {vpc_id}")
    except Exception as error:
        print(f"Failed to delete VPC. Error: {error}")
