import boto3
from aws_manager.nandita_1_vpc import create_vpc
from aws_manager.nandita_2_subnet import create_subnets
from aws_manager.nandita_3_internet_gateway import create_and_attach_internet_gateway
from aws_manager.nandita_4_route_table import update_route_tables
from aws_manager.nandita_5_security_group import create_security_group
from aws_manager.nandita_6_db_subnet_group import create_db_subnet_group
from aws_manager.nandita_7_ec2 import create_ec2_instance
from aws_manager.nandita_8_rds import create_rds_instance


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
