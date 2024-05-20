import boto3

def create_ec2_instance(config, subnet_id, security_group_id): 
    ec2_resource = boto3.resource('ec2')
    try:
        instance = ec2_resource.create_instances(ImageId=config['ami'], InstanceType=config['instance_type'], MinCount=1, MaxCount=1, SubnetId=subnet_id, SecurityGroupIds=[security_group_id], TagSpecifications=[{'ResourceType': 'instance', 'Tags': [{'Key': 'Name', 'Value': 'NanditaInstance'}]}])[0]
        print(f"Nandita's EC2 Instance Created with ID: {instance.id}")
        return instance
    except Exception as error:
        print(f"Failed to create EC2 instance. Error: {error}")