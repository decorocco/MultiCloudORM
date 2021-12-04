import boto3
from botocore.config import Config

def create_sec_group(client, name, sec_rules):
    vpcs = client.describe_vpcs()
    id = vpcs['Vpcs'][0]['VpcId']

    try:
        security_group = client.create_security_group(GroupName=name,Description="Script Deco",VpcId=id)
    except Exception as e:
        print(e)

    sec_group_id = security_group['GroupId']
    client.authorize_security_group_ingress(
        GroupId=sec_group_id,
        IpPermissions = sec_rules
    )
    print(f"{name} created")
    return sec_group_id


def create_instance(client, image, instance_name, key_name, script, sec_group_name, sec_group_id):
    print(f"Creating instance '{instance_name}'")

    if script == None:
        instances = client.run_instances(
            ImageId=image,
            MinCount=1,
            MaxCount=1,
            InstanceType="t2.micro",
            KeyName=key_name,
            SecurityGroupIds=[sec_group_id],
            SecurityGroups=[sec_group_name]
        )

    else:
        instances = client.run_instances(
            ImageId=image,
            MinCount=1,
            MaxCount=1,
            InstanceType="t2.micro",
            KeyName=key_name,
            UserData = script,
            SecurityGroupIds=[sec_group_id],
            SecurityGroups=[sec_group_name],
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": [{"Key": "Name", "Value": instance_name}]
                }
            ]
        )

    for i in instances['Instances']:
        if i['KeyName'] == key_name:
            instance_id = i['InstanceId']

    waiter = client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=[instance_id])
    print(f"Instance id = {instance_id}")
    return instance_id


def get_instance_ip(client, key_name):

    ip = client.describe_instances(Filters=[
        {
            'Name': 'key-name',
            'Values': [
                key_name,
            ]
        },
        {
            'Name': 'instance-state-name',
            'Values': [
                "running"
            ]
        },
    ],
    )['Reservations'][0]['Instances'][0]['PublicIpAddress']

    print(f"Public ip = {ip}")
    print("")

    return ip


def create_image(client, instance_id, name_image):
    print(f"Creating Image {name_image} from instance {instance_id}")
    image=client.create_image(InstanceId=instance_id,Name=name_image)
    waiter = client.get_waiter('image_available')
    image_id = image["ImageId"]
    waiter.wait(ImageIds=[image_id])
    print(f"Image {name_image} created, id = {image_id}")
    return image_id


def create_load_balancer(client,client_lb,lb_name,sec_group_id):    
    subnets = client.describe_subnets()
    subnets_id = []
    for subnet in subnets['Subnets']:
        subnets_id.append(subnet['SubnetId'])
    waiter = client_lb.get_waiter('load_balancer_available')
    print(f"Creating {lb_name}")
    load_balancer_created = client_lb.create_load_balancer(Name = lb_name,
                                                                    Subnets=subnets_id,
                                                                    SecurityGroups=[sec_group_id],
                                                                    IpAddressType="ipv4",)
    LoadBalancerArn_ = load_balancer_created['LoadBalancers'][0]['LoadBalancerArn']
    LoadBalancerDNS = load_balancer_created['LoadBalancers'][0]['DNSName']
    waiter.wait(LoadBalancerArns=[LoadBalancerArn_])
    print(f"{lb_name} created")
    return LoadBalancerArn_


def create_target_group(client,client_lb,tg_name):
    vpc_id = client.describe_vpcs()['Vpcs'][0]['VpcId']
    tg=client_lb.create_target_group(
        Name = tg_name,
        Protocol = 'HTTP',
        Port = 8080,
        TargetType='instance',
        VpcId = vpc_id,
        HealthCheckPath='/tasks/'
    )
    tg_arn =tg['TargetGroups'][0]['TargetGroupArn']
    print(f"Target group {tg_name} created, Arn = {tg_arn}")
    return tg_arn


def create_launch_configuration(client,launch_config_name,image_id,sec_group_id,key_name):
    print(f"Creating Launch Configuration: {launch_config_name}")   
    try:
        client.create_launch_configuration(
            LaunchConfigurationName=launch_config_name,
            ImageId=image_id,
            SecurityGroups=[sec_group_id],
            InstanceType='t2.micro',
            KeyName=key_name
        )
    except:
        print(f"{launch_config_name} already exists")
        return
    print(f"Launch Configuration {launch_config_name} created")


def create_auto_scaling_group(client,client_as,as_name,launch_config_name,tg_arn):
    print(f"Creating AutoScaling Group '{as_name}'")
    list_zones = []
    for zones in client.describe_availability_zones()['AvailabilityZones']:
        list_zones.append(zones['ZoneName'])
    auto_scaling = client_as.create_auto_scaling_group(
        AutoScalingGroupName=as_name,
        LaunchConfigurationName=launch_config_name,
        MinSize=1,
        MaxSize = 3,
        TargetGroupARNs=[tg_arn],
        AvailabilityZones = list_zones
    )
    print(f"Autoscaling Group '{as_name}' created")
  
    try:
        print("Attaching load balancer")
        client_as.attach_load_balancer_target_groups(
        AutoScalingGroupName=as_name,
        TargetGroupARNs=[
            tg_arn
        ]
        )
        print("Load balancer attached")
        return
    except Exception as e:
        print("ERROR")
        print(e)
        return False


def create_listener(client,load_balancer_arn,tg_arn):
    print("Creating listener on port: 80")
    listener_created=client.create_listener(
        LoadBalancerArn= load_balancer_arn,
        Protocol='HTTP',
        Port=80,
        DefaultActions=[
            {
                'Type': 'forward',
                'TargetGroupArn': tg_arn

            }
        ]
    )
    listener_arn = listener_created['Listeners'][0]['ListenerArn']
    print("Listener created")
    return listener_arn


def create_policy(client, as_group_name, target_group_arn, load_balancer_arn):
  try: 
    print("")
    print("Creating AutoScaling Policy")
    load_balancer_name = load_balancer_arn[load_balancer_arn.find("app"):]
    target_group_name = target_group_arn[target_group_arn.find("targetgroup"):]
    client.put_scaling_policy(
      AutoScalingGroupName=as_group_name,
      PolicyName="TargetTrackingScaling",
      PolicyType="TargetTrackingScaling",
      TargetTrackingConfiguration={
        "PredefinedMetricSpecification": {
          "PredefinedMetricType": "ALBRequestCountPerTarget",
          "ResourceLabel": f"{load_balancer_name}/{target_group_name}"
        },
        "TargetValue": 50
      }
    )
    print("Policy created")
  except:
    print("ERROR: Could not create policy")