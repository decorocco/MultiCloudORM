import os
import boto3
import time
from createFunctions import *
from delFunctions import *
from SecRules import *
from instanceScripts import *

#variables

NORTH_VIRGINIA_REGION = "us-east-1"
OHIO_REGION = "us-east-2"
AMI_NORTH_VIRGINIA_ID = "ami-0279c3b3186e54acd"
AMI_OHIO_ID = "ami-020db2c14939a8efb"
KEY_PAIR_NAME_NV = "Deco"
KEY_PAIR_NAME_OHIO = "Deco-Ohio"
IMAGE_NAME = "Django-Image-Deco"
TARGET_GROUP_NAME = "Target-Group-Deco"
LOAD_BALANCER_NAME = "Load-Balancer-Deco"
LAUNCH_CONFIG_NAME = "Launch-Config-Deco"
AS_GROUP_NAME = "Auto-Scaling-Deco"
POLICY_NAME = "Policy-Deco"

sec_group_db_name = "sec_group_database"
sec_group_django_name = "sec_group_django"
sec_group_names = [sec_group_db_name, sec_group_django_name]

ec2_north_virginia = boto3.client('ec2', region_name=NORTH_VIRGINIA_REGION)
ec2_ohio = boto3.client('ec2', region_name=OHIO_REGION)
load_balancer = boto3.client('elbv2', region_name=NORTH_VIRGINIA_REGION)
auto_scaling = boto3.client('autoscaling', region_name=NORTH_VIRGINIA_REGION)

######################################################################
#deleting

waiter_del_lb = load_balancer.get_waiter('load_balancers_deleted')
delete_load_balancer(load_balancer, LOAD_BALANCER_NAME, waiter_del_lb)
print("")

time.sleep(30)

delete_auto_scaling_group(auto_scaling, AS_GROUP_NAME)
print("")

delete_image(ec2_north_virginia, IMAGE_NAME)

delete_launch_configuration(auto_scaling, LAUNCH_CONFIG_NAME)
print("")

instances_to_delete_nv = delete_instances(ec2_north_virginia, KEY_PAIR_NAME_NV)
instances_to_delete_ohio = delete_instances(ec2_ohio, KEY_PAIR_NAME_OHIO)
print("")

delete_target_group(load_balancer, TARGET_GROUP_NAME)
print("")

delete_sec_groups(ec2_north_virginia, sec_group_names)
delete_sec_groups(ec2_ohio, sec_group_names)
print("")

######################################################################
#creating

sec_group_id_db = create_sec_group(ec2_ohio, sec_group_db_name, Sec_Rules_Database)
sec_group_id_django = create_sec_group(ec2_north_virginia, sec_group_django_name, Sec_Rules_Django)
print("")

database_id = create_instance(ec2_ohio, 
                                AMI_OHIO_ID,
                                "database-deco",
                                KEY_PAIR_NAME_OHIO,
                                database_script,
                                sec_group_db_name,
                                sec_group_id_db)

database_ip = get_instance_ip(ec2_ohio, KEY_PAIR_NAME_OHIO)

django_script=f"""
#cloud-config
runcmd:
- cd /home/ubuntu
- sudo apt update -y
- git clone https://github.com/decorocco/tasks.git
- cd tasks
- sed -i "s/node1/{database_ip}/g" ./portfolio/settings.py
- ./install.sh
- sudo ufw allow 8080/tcp -y
- sudo reboot
"""
                                        
django_id = create_instance(ec2_north_virginia, 
                                AMI_NORTH_VIRGINIA_ID,
                                "django-deco",
                                KEY_PAIR_NAME_NV,
                                django_script,
                                sec_group_django_name,
                                sec_group_id_django)

django_ip = get_instance_ip(ec2_north_virginia, KEY_PAIR_NAME_NV)

time.sleep(60)

AMI_django_id = create_image(ec2_north_virginia, django_id, IMAGE_NAME)
print("")

instances_to_wait_nv = delete_instances(ec2_north_virginia, KEY_PAIR_NAME_NV)
print("")

target_group_arn = create_target_group(ec2_north_virginia, load_balancer, TARGET_GROUP_NAME)

load_balancer_arn = create_load_balancer(ec2_north_virginia,
                                            load_balancer, 
                                            LOAD_BALANCER_NAME, 
                                            sec_group_id_django)

create_launch_configuration(auto_scaling, 
                            LAUNCH_CONFIG_NAME, 
                            AMI_django_id, 
                            sec_group_id_django, 
                            KEY_PAIR_NAME_NV)

create_auto_scaling_group(ec2_north_virginia, 
                            auto_scaling, 
                            AS_GROUP_NAME, 
                            LAUNCH_CONFIG_NAME, 
                            target_group_arn)

listener_arn = create_listener(load_balancer, load_balancer_arn, target_group_arn)

policy = create_policy(auto_scaling, AS_GROUP_NAME, target_group_arn, load_balancer_arn)