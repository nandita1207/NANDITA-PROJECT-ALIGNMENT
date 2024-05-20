import boto3

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