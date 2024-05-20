import boto3
def create_and_attach_internet_gateway(ec2_client, vpc_id): #networking element 3 - internal gateway
    try:
        igw = ec2_client.create_internet_gateway()
        igw_id = igw['InternetGateway']['InternetGatewayId']
        ec2_client.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
        print(f"Internet Gateway Created and Attached with ID: {igw_id}")
        return igw_id
    except Exception as error:
        print(f"Failed to create and attach internet gateway. Error: {error}")