import boto3

def update_route_tables(ec2_client, vpc_id, igw_id): #networking element 4 - route tables
    try:
        route_tables = ec2_client.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['RouteTables']
        for rt in route_tables:
            ec2_client.create_route(RouteTableId=rt['RouteTableId'], DestinationCidrBlock='0.0.0.0/0', GatewayId=igw_id)
            print(f"Route added to {rt['RouteTableId']} to route traffic via {igw_id}")
    except Exception as error:
        print(f"Failed to update route tables. Error: {error}")