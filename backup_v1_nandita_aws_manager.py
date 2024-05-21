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

def create_subnets(vpc_id): #networking_element_1_vpc
    ec2_client = boto3.client('ec2')
    try:
        azs = ec2_client.describe_availability_zones()['AvailabilityZones']
        subnet_ids = []
        for i, az in enumerate(azs):
            if i == 2:  # 2 is for simplicity
                break
            subnet_response = ec2_client.create_subnet(CidrBlock=f"10.0.{i}.0/24", VpcId=vpc_id, AvailabilityZone=az['ZoneName'])
            subnet = subnet_response['Subnet']
            print(f"Subnet Created in {az['ZoneName']} with ID: {subnet['SubnetId']}")
            subnet_ids.append(subnet['SubnetId'])
        return subnet_ids
    except Exception as error:
        print(f"Failed to create subnets. Error: {error}")

def create_and_attach_internet_gateway(ec2_client, vpc_id): #networking element 2 - internal gateway
    try:
        igw = ec2_client.create_internet_gateway()
        igw_id = igw['InternetGateway']['InternetGatewayId']
        ec2_client.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
        print(f"Internet Gateway Created and Attached with ID: {igw_id}")
        return igw_id
    except Exception as error:
        print(f"Failed to create and attach internet gateway. Error: {error}")

def update_route_tables(ec2_client, vpc_id, igw_id): #networking element 4 - route tables
    try:
        route_tables = ec2_client.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['RouteTables']
        for rt in route_tables:
            ec2_client.create_route(RouteTableId=rt['RouteTableId'], DestinationCidrBlock='0.0.0.0/0', GatewayId=igw_id)
            print(f"Route added to {rt['RouteTableId']} to route traffic via {igw_id}")
    except Exception as error:
        print(f"Failed to update route tables. Error: {error}")

def create_security_group(vpc_id, description, name_suffix): #networking element 5 - security group
    ec2_client = boto3.client('ec2')
    try:
        sg_response = ec2_client.create_security_group(GroupName=f'NanditaSG-{name_suffix}', Description=description, VpcId=vpc_id)
        security_group_id = sg_response['GroupId']
        ec2_client.authorize_security_group_ingress(GroupId=security_group_id, IpPermissions=[{'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}])
        print(f"Security Group {name_suffix} Created with ID: {security_group_id}")
        return security_group_id
    except Exception as error:
        print(f"Failed to create security group. Error: {error}")
 
def create_db_subnet_group(description, name, subnet_ids): #networking element 6 - db's subnet group
    rds_client = boto3.client('rds')
    try:
        response = rds_client.create_db_subnet_group(DBSubnetGroupName=name, DBSubnetGroupDescription=description, SubnetIds=subnet_ids)
        print(f"DB Subnet Group Created with Name: {name}")
        return name
    except Exception as error:
        print(f"Failed to create DB subnet group. Error: {error}")

def create_ec2_instance(config, subnet_id, security_group_id): 
    ec2_resource = boto3.resource('ec2')
    try:
        instance = ec2_resource.create_instances(ImageId=config['ami'], InstanceType=config['instance_type'], MinCount=1, MaxCount=1, SubnetId=subnet_id, SecurityGroupIds=[security_group_id], TagSpecifications=[{'ResourceType': 'instance', 'Tags': [{'Key': 'Name', 'Value': 'NanditaInstance'}]}])[0]
        print(f"Nandita's EC2 Instance Created with ID: {instance.id}")
        return instance
    except Exception as error:
        print(f"Failed to create EC2 instance. Error: {error}")

def create_rds_instance(config, db_subnet_group_name, security_group_id):
    rds_client = boto3.client('rds')
    try:
        db_instance = rds_client.create_db_instance(DBInstanceIdentifier='nandita-db-instance', AllocatedStorage=config['allocated_storage'], DBInstanceClass=config['instance_class'], Engine=config['engine'], MasterUsername=config['username'], MasterUserPassword=config['password'], DBSubnetGroupName=db_subnet_group_name, VpcSecurityGroupIds=[security_group_id], MultiAZ=False, EngineVersion=config['engine_version'], PubliclyAccessible=True)
        print(f"Nandita's RDS Instance Created with ID: {db_instance['DBInstance']['DBInstanceIdentifier']}")
        return db_instance
    except Exception as error:
        print(f"Failed to create RDS instance. Error: {error}")

#Destroy fucntions

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


def delete_db_subnet_group(db_subnet_group_name):
    rds_client = boto3.client('rds')
    try:
        rds_client.delete_db_subnet_group(DBSubnetGroupName=db_subnet_group_name)
        print(f"Deleted DB Subnet Group named: {db_subnet_group_name}")
    except Exception as error:
        print(f"Failed to delete DB Subnet Group. Error: {error}")


def delete_ec2_instance(instance_id):
    ec2_resource = boto3.resource('ec2')
    instance = ec2_resource.Instance(instance_id)
    try:
        instance.terminate()  # or instance.stop() if you want to stop instead of terminate
        print(f"Terminated EC2 Instance with ID: {instance_id}")
    except Exception as error:
        print(f"Failed to terminate EC2 Instance. Error: {error}")


def delete_rds_instance(db_instance_identifier):
    rds_client = boto3.client('rds')
    try:
        rds_client.delete_db_instance(DBInstanceIdentifier=db_instance_identifier, SkipFinalSnapshot=True)
        print(f"Deleted RDS Instance with Identifier: {db_instance_identifier}")
    except Exception as error:
        print(f"Failed to delete RDS Instance. Error: {error}")








def apply_configuration(config):
    print("Applying Nandita's configuration...")
    ec2_client = boto3.client('ec2')
    aws_resources = config.get('aws_resources', {})
    if 'vpc' in aws_resources:
        vpc = create_vpc(aws_resources['vpc'])
        subnet_ids = create_subnets(vpc['VpcId'])
        ec2_sg = create_security_group(vpc['VpcId'], 'Security group for EC2 instances', 'ec2')
        rds_sg = create_security_group(vpc['VpcId'], 'Security group for RDS instances', 'rds')
        db_subnet_group_name = create_db_subnet_group('Subnet group for RDS instances', 'NanditaDBSubnetGroup', subnet_ids)
        igw_id = create_and_attach_internet_gateway(ec2_client, vpc['VpcId'])
        update_route_tables(ec2_client, vpc['VpcId'], igw_id)
    if 'ec2' in aws_resources:
        instance = create_ec2_instance(aws_resources['ec2'], subnet_ids[0], ec2_sg)
    if 'rds' in aws_resources and db_subnet_group_name:
        db_instance = create_rds_instance(aws_resources['rds'], db_subnet_group_name, rds_sg)
    else:
        print("Skipping RDS instance creation due to issues with DB subnet group or other dependencies.")
    print("Yay!! Nandita's Configuration application complete.")


def destroy_configuration(state):
    print("Destroying configuration...")
    if 'vpc_id' in state:
        delete_vpc(state['vpc_id'])
    if 'ec2_id' in state:
        delete_ec2_instance(state['ec2_id'])
    if 'rds_id' in state:
        delete_rds_instance(state['rds_id'])
    print("Configuration destruction complete.")