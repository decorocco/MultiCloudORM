import os

def delete_sec_groups(client, sec_group_name):
  try:
    print("Deleting Security Group")
    security_groups = client.describe_security_groups()

    for security_group in security_groups["SecurityGroups"]:
      if security_group["GroupName"] in sec_group_name:
        client.delete_security_group(GroupId=security_group["GroupId"])
        print("Security Group deleted")
        print("")

  except Exception as e:
    print("")
    print("ERROR:")
    print(e)


def delete_instances(client,key_pair):
    instances_id = []
    waiter = client.get_waiter('instance_terminated')
    for i in client.describe_instances(Filters=[
        {
            'Name': 'key-name',
            'Values': [
                key_pair,
            ]
        },
        {
            'Name': 'instance-state-name',
            'Values': [
                "pending","running","stopping","stopped"
            ]
        },
    ],
)['Reservations']:
        instances_id.append(i['Instances'][0]["InstanceId"])

    if len(instances_id) > 0:
        print(f"Deleting Instance with id: {instances_id}")
        client.terminate_instances(InstanceIds=instances_id)
        waiter.wait(InstanceIds=instances_id)
        print(f"Instance with id {instances_id} deleted")
        return instances_id

    else:
        print(f"No Instances with keypair {key_pair} found")
        

def delete_image(client,image_name):
    print(f"Deleting {image_name}")
    images=client.describe_images(Filters=[
        {
            'Name': 'name',
            'Values': [
                image_name,
            ]
        },
    ])
    if len(images['Images'])<1:
        print(f"No Images called {image_name}")
        print("")
        return
    image_id = images['Images'][0]['ImageId']
    client.deregister_image(ImageId=image_id)
    print(f"Image {image_name} deleted")
    print("")


def delete_load_balancer(client, lb_name, waiter):
  try:
    load_balancer = client.describe_load_balancers()
    if len(load_balancer['LoadBalancers']) > 0:
      for lb in load_balancer['LoadBalancers']:
        if lb["LoadBalancerName"] == lb_name:
          client.delete_load_balancer(LoadBalancerArn=lb["LoadBalancerArn"])
          print("")
          print("Deleting Load Balancer")
          
          waiter.wait(LoadBalancerArns=[lb["LoadBalancerArn"]])
          print("Load Balancer Deleted")

    else:
      print(f"No Load Balancer called {lb_name}")
      return

  except Exception as e:
    print("ERROR")
    print(e)
    return False


def delete_target_group(client,tg_name):
    print(f"Deleting Target Group {tg_name}")
    try:
        target_gp=client.describe_target_groups(Names=[tg_name])
    except:
        print(f"No Target Group called {tg_name}")
        return
    tg_arn = target_gp['TargetGroups'][0]['TargetGroupArn']
    client.delete_target_group(TargetGroupArn = tg_arn)
    print(f"Target Group {tg_name} deleted")


def delete_launch_configuration(client,launch_config_name):
    print(f"Deleting Launch Configuration {launch_config_name}")
    try:        
        client.delete_launch_configuration(
            LaunchConfigurationName = launch_config_name
        )
    except:
        print(f"No Launch Configuration called {launch_config_name}")
        return
    print(f"Launch Configuration {launch_config_name} deleted")


def delete_auto_scaling_group(client,as_name):
    print(f"Deleting AutoScaling group {as_name}")
    try:
        client.delete_auto_scaling_group(AutoScalingGroupName = as_name,ForceDelete= True)
        print(f"AutoScaling group {as_name} deleted")
    except:
        print(f"No AutoScaling Group called {as_name}")
