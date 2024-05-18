import boto3

def create_vpc(config):
    ec2_client = boto3.client('ec2')
    vpc_response = ec2_client.create_vpc(CidrBlock=config['cidr_block'])
    vpc = vpc_response['Vpc']
    print(f"VPC Created with ID: {vpc['VpcId']}")
    return vpc

def create_subnets(vpc_id):
    ec2_client = boto3.client('ec2')
    azs = ec2_client.describe_availability_zones()['AvailabilityZones']
    subnet_ids = []
    for i, az in enumerate(azs):
        if i == 2:  # Limit to two subnets for simplicity
            break
        subnet_response = ec2_client.create_subnet(
            CidrBlock=f"10.0.{i}.0/24",
            VpcId=vpc_id,
            AvailabilityZone=az['ZoneName']
        )
        subnet = subnet_response['Subnet']
        print(f"Subnet Created in {az['ZoneName']} with ID: {subnet['SubnetId']}")
        subnet_ids.append(subnet['SubnetId'])
    return subnet_ids


def create_security_group(vpc_id, description, name_suffix):
    ec2_client = boto3.client('ec2')
    sg_response = ec2_client.create_security_group(GroupName=f'NanditaSG-{name_suffix}', Description=description, VpcId=vpc_id)
    security_group = sg_response['GroupId']
    # Open up SSH access
    ec2_client.authorize_security_group_ingress(
        GroupId=security_group,
        IpPermissions=[{'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
    ])
    print(f"Security Group {name_suffix} Created with ID: {security_group}")
    return security_group

def create_db_subnet_group(description, name, subnet_ids):
    rds_client = boto3.client('rds')
    try:
        response = rds_client.create_db_subnet_group(
            DBSubnetGroupName=name,
            DBSubnetGroupDescription=description,
            SubnetIds=subnet_ids
        )
        print(f"DB Subnet Group Created with Name: {name}")
        return response['DBSubnetGroup']
    except Exception as e:
        print(f"Failed to create DB subnet group: {e}")

def create_and_attach_internet_gateway(ec2_client, vpc_id):
    igw = ec2_client.create_internet_gateway()
    igw_id = igw['InternetGateway']['InternetGatewayId']
    ec2_client.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
    print(f"Internet Gateway Created and Attached with ID: {igw_id}")
    return igw_id

def update_route_tables(ec2_client, vpc_id, igw_id):
    route_tables = ec2_client.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['RouteTables']
    for rt in route_tables:
        ec2_client.create_route(RouteTableId=rt['RouteTableId'], DestinationCidrBlock='0.0.0.0/0', GatewayId=igw_id)
        print(f"Route added to {rt['RouteTableId']} to route traffic via {igw_id}")



def create_ec2_instance(config, subnet_id, security_group_id):
    ec2_resource = boto3.resource('ec2')
    instance = ec2_resource.create_instances(
        ImageId=config['ami'],
        InstanceType=config['instance_type'],
        MinCount=1,
        MaxCount=1,
        SubnetId=subnet_id,
        SecurityGroupIds=[security_group_id],
        TagSpecifications=[{'ResourceType': 'instance', 'Tags': [{'Key': 'Name', 'Value': 'NanditaInstance'}]}]
    )[0]
    print(f"EC2 Instance Created with ID: {instance.id}")
    return instance

def create_rds_instance(config, db_subnet_group_name, security_group_id):
    rds_client = boto3.client('rds')
    try:
        db_instance = rds_client.create_db_instance(
            DBInstanceIdentifier='nandita-db-instance',
            AllocatedStorage=config['allocated_storage'],
            DBInstanceClass=config['instance_class'],
            Engine=config['engine'],
            MasterUsername='admin',
            MasterUserPassword='nanditasolacedb',  # my db password - Acknowledging  this is not a best practice in prod
            DBSubnetGroupName=db_subnet_group_name,
            VpcSecurityGroupIds=[security_group_id],
            MultiAZ=False,
            EngineVersion=config['engine_version'],
            PubliclyAccessible=True
        )
        print(f"RDS Instance Created with ID: {db_instance['DBInstance']['DBInstanceIdentifier']}")
        return db_instance
    except Exception as e:
        print(f"Failed to create RDS instance: {e}")

def apply_configuration(config):
    print("Applying configuration...")
    ec2_client = boto3.client('ec2')
    aws_resources = config.get('aws_resources', {})
    if 'vpc' in aws_resources:
        vpc = create_vpc(aws_resources['vpc'])
        subnet_ids = create_subnets(vpc['VpcId'])
        ec2_sg = create_security_group(vpc['VpcId'], 'Security group for EC2 instances', 'ec2')
        rds_sg = create_security_group(vpc['VpcId'], 'Security group for RDS instances', 'rds')
        db_subnet_group = create_db_subnet_group('Subnet group for RDS instances', 'NanditaDBSubnetGroup', subnet_ids)
        igw_id = create_and_attach_internet_gateway(ec2_client, vpc['VpcId'])
        update_route_tables(ec2_client, vpc['VpcId'], igw_id)
    if 'ec2' in aws_resources:
        instance = create_ec2_instance(aws_resources['ec2'], subnet_ids[0], ec2_sg)
    if 'rds' in aws_resources:
        db_instance = create_rds_instance(aws_resources['rds'], db_subnet_group['DBSubnetGroupName'], rds_sg)
    print("Configuration application complete.")


