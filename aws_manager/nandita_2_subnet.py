import boto3

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