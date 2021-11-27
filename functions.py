import boto3
from botocore.config import Config

def create_sec_group(client, name, sec_rules):
    vpcs = client.describe_vpcs()
    vpc_id = vpcs['Vpcs'][0]['VpcId']

    try:
        security_group = client.create_security_group(GroupName=name,Description="Script Deco",VpcId=vpc_id)
    except Exception as e:
        print(e)

    sec_group_id = security_group['GroupId']
    client.authorize_security_group_ingress(
        GroupId=sec_group_id,
        IpPermissions = sec_rules
    )
    print(f"Security Group {name} created")
    return sec_group_id