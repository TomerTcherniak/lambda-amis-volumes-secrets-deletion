import os
import time
import traceback
from datetime import datetime, timedelta
import logging
import boto3


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s  [%(filename)s#%(lineno)s]')
logger = logging.getLogger("LAMDA-AMIS-VOLS-TO-BE-DELETED")
logger.setLevel("INFO")

__author__ = "Tomer Tcherniak"

def log_print(msg):
    logger.info(msg)


def calculate_volumes_to_be_deleted(aws_region):

    sts = boto3.client("sts")
    account_id = sts.get_caller_identity()["Account"]
    log_print(
        "*################## Volume Region ############# : {0} {1}".format(aws_region, account_id))

    ec2_client = boto3.client('ec2', region_name=aws_region)
    ec2_resource = boto3.resource('ec2', region_name=aws_region)

    available_vol_response = ec2_client.describe_volumes(
        Filters=[
            {
                'Name': 'status',
                'Values': ['available',]
            },
        ],
    )
    older_threshold_time = datetime.now() - timedelta(days=int(30))
    s_older_threshold_time = datetime(
        older_threshold_time.year, older_threshold_time.month, older_threshold_time.day, 0, 0)
    volume_list = []
    for volume_info in available_vol_response['Volumes']:
        s_create_time = datetime(
            volume_info['CreateTime'].year, volume_info['CreateTime'].month, volume_info['CreateTime'].day, 0, 0)
        try:
            name = None
            vol = ec2_resource.Volume(id=volume_info['VolumeId'])
            for tag in vol.tags:
                if tag['Key'] == 'Name':
                    name = tag.get('Value')
        except:
            continue

        for tag in vol.tags:
            if tag['Key'] == 'Name':
                name = tag.get('Value')
        if s_create_time < s_older_threshold_time:
            try:
                volume_list.append({"VolumeId" : volume_info['VolumeId'] ,"Size" : str(volume_info['Size']) , "CreateTime" : str(volume_info['CreateTime']) , "Name" : name})
            except Exception as exception:
                log_print("Error Reported : " + str(exception))

    if len(volume_list) > 0:
        log_print("_# Volumes in {0} , account id {1} , length volumes to b deleted".format(aws_region,account_id,str(len(volume_list))))
        for volume in volume_list:
            time.sleep(0.5)
            ec2_resource = boto3.resource('ec2', region_name=aws_region)
            volume_resource = ec2_resource.Volume(volume["VolumeId"])
            if  volume_resource.state == "available":
                #volume_resource.delete()
                log_print("Deleted Volume in {} {} , VolumeId {} , Size {} , CreateTime {} , Name {}".format(aws_region,account_id,volume["VolumeId"],volume["Size"],volume["CreateTime"],volume["Name"]))


def secret_deletion(aws_region):

    sts = boto3.client("sts")
    account_id = sts.get_caller_identity()["Account"]
    log_print(
        "*################## Secret Region ############# : {0} {1}".format(aws_region, account_id))

    days_count = 180
    results_for_call = 100
    client = boto3.client('secretsmanager', region_name=aws_region)
    response = client.list_secrets()
    older_threshold_time = datetime.now() - timedelta(days=int(days_count))
    s_older_threshold_time = datetime(
        older_threshold_time.year, older_threshold_time.month, older_threshold_time.day, 0, 0)
    while True:
        if 'NextToken' in response:
            response = client.list_secrets(
                MaxResults=results_for_call, NextToken=response['NextToken'])
        else:
            response = client.list_secrets(MaxResults=results_for_call)
        for secret in response['SecretList']:
            try:
                s_create_time = datetime(
                    secret['CreatedDate'].year, secret['CreatedDate'].month, secret['CreatedDate'].day, 0, 0)
                delta = s_older_threshold_time - s_create_time
                if delta.days < 0:
                    continue
                if secret['LastAccessedDate'] is not None:
                    s_access_time = datetime(
                        secret['LastAccessedDate'].year, secret['LastAccessedDate'].month, secret['LastAccessedDate'].day, 0, 0)
                    delta = s_older_threshold_time - s_access_time
                    if delta.days < 0:
                        continue
                    #client.delete_secret(SecretId=secret['Name'], RecoveryWindowInDays=10, ForceDeleteWithoutRecovery=False)
            except:
                continue
        if 'NextToken' not in response:
            break


def calculate_amis_to_be_deleted(aws_region):

    sts = boto3.client("sts")
    account_id = sts.get_caller_identity()["Account"]
    log_print(
        "*################## AMI Region ############# : {0} {1}".format(aws_region, account_id))

    images_to_be_deleted = []
    launch_config_ami = []
    autoscaling = boto3.client('autoscaling', region_name=aws_region)
    ec2_conn = boto3.client('ec2', region_name=aws_region)
    launch_configurations = autoscaling.describe_launch_configurations()
    images_list = ec2_conn.describe_images(Owners=[account_id])
    snapshots = ec2_conn.describe_snapshots(OwnerIds=[account_id])['Snapshots']

    for launch_configuration in launch_configurations['LaunchConfigurations']:
        launch_config_ami.append(launch_configuration['ImageId'])

    for image in images_list['Images']:
        try:
            if image['ImageId'] not in launch_config_ami:
                image_name = image['Name']
                image_id = image['ImageId']
                image_date = datetime.strptime(
                    image['CreationDate'], '%Y-%m-%dT%H:%M:%S.%fZ')
                ami_age_limit = datetime.now() - timedelta(hours=180)
                print ({ "ImageID" : image_id , "ImageDate" : image_date , "ImageName" : image_name })
                if image_date < ami_age_limit:
                    images_to_be_deleted.append({ "ImageID" : image_id , "ImageDate" : image_date , "ImageName" : image_name })
        except:
            #print (image['ImageId'])
            # traceback.print_exc()
            pass

    snapshots = ec2_conn.describe_snapshots(OwnerIds=[account_id])['Snapshots']
    if len(images_to_be_deleted) > 0:
        log_print("_# Images in {} {} , Length to be deleted {}".format(aws_region,account_id,str(len(images_to_be_deleted))))
    for image_to_be_delete in images_to_be_deleted:
            images_list = ec2_conn.describe_images(
                Filters=[{'Name': 'image-id', 'Values': [image_to_be_delete["ImageID"]]}])
            for image in images_list['Images']:
                if "ami" in image['ImageId']:
                    time.sleep(0.1)
                    log_print("Deleted AMI info {}".format(image_to_be_delete))
                    #ec2_conn.deregister_image(ImageId=image['ImageId'])
                    for snapshot in snapshots:
                        if str(image['ImageId']) in snapshot['Description']:
                            #ec2_conn.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
                            log_print("Deleted snapshot info {}".format(snapshot))

def main(regions_arr):
    for aws_region in regions_arr:
        time.sleep(0.1)
        calculate_amis_to_be_deleted(aws_region)
        secret_deletion(aws_region)
        calculate_volumes_to_be_deleted(aws_region)

def lambda_handler(event, context):
    regions_arr = os.environ['regions_arr'].split(",")
    main(regions_arr)
