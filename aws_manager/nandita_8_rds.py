import boto3

def create_rds_instance(config, db_subnet_group_name, security_group_id):
    rds_client = boto3.client('rds')
    try:
        db_instance = rds_client.create_db_instance(DBInstanceIdentifier='nandita-db-instance', AllocatedStorage=config['allocated_storage'], DBInstanceClass=config['instance_class'], Engine=config['engine'], MasterUsername=config['username'], MasterUserPassword=config['password'], DBSubnetGroupName=db_subnet_group_name, VpcSecurityGroupIds=[security_group_id], MultiAZ=False, EngineVersion=config['engine_version'], PubliclyAccessible=True)
        print(f"Nandita's RDS Instance Created with ID: {db_instance['DBInstance']['DBInstanceIdentifier']}")
        return db_instance
    except Exception as error:
        print(f"Failed to create RDS instance. Error: {error}")
