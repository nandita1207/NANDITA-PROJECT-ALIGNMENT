import boto3

def create_db_subnet_group(description, name, subnet_ids): #networking element 6 - db's subnet group
    rds_client = boto3.client('rds')
    try:
        response = rds_client.create_db_subnet_group(DBSubnetGroupName=name, DBSubnetGroupDescription=description, SubnetIds=subnet_ids)
        print(f"DB Subnet Group Created with Name: {name}")
        return name
    except Exception as error:
        print(f"Failed to create DB subnet group. Error: {error}")
