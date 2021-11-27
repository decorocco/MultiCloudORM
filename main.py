import os
import boto3
from functions import *
from SecRules import *

NORTH_VIRGINIA_REGION = "us-east-1"
OHIO_REGION = "us-east-2"
AMI_ID_NORTH_VIRGINIA_ID="ami-0279c3b3186e54acd"
AMI_ID_OHIO_ID="ami-020db2c14939a8efb"

sec_group_db_name = "sec_group_database"
sec_group_django_name = "sec_group_django"

######################################################################

ec2_north_virginia_ = boto3.client('ec2', region_name=NORTH_VIRGINIA_REGION)
ec2_ohio = boto3.client('ec2', region_name=OHIO_REGION)

sec_group_id_db = create_sec_group(ec2_ohio, sec_group_db_name, Sec_Rules_Database)
sec_group_id_django = create_sec_group(ec2_north_virginia_, sec_group_django_name, Sec_Rules_Django)