import boto3
import json
import operator
import json
import time
import os
import traceback
from urllib import request
from datetime import datetime, timedelta
from collections import Counter
import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s  [%(filename)s#%(lineno)s]')
logger = logging.getLogger("lambda-amis-autoscaling-to-be-deleted")
logger.setLevel("INFO")

__author__ = "Tomer Tcherniak"


def debugPrint(msg):
    logger.info(msg)
    print(msg)


def calculate_volumes_to_be_deleted(use_profile, days_count, AWS_REGION, delete_flag, account_id):

    print("calculate_volumes_to_be_deleted")
    if use_profile == "true":
        boto3.setup_default_session(profile_name='rnd')

    ec2_client = boto3.client('ec2', region_name=AWS_REGION)
    ec2_resource = boto3.resource('ec2', region_name=AWS_REGION)
    available_vol_response = ec2_client.describe_volumes(
        Filters=[
            {
                'Name': 'status',
                'Values': [
                        'available',
                ]
            },
        ],
    )
    older_threshold_time = datetime.now() - timedelta(days=int(days_count))
    s_older_threshold_time = datetime(
        older_threshold_time.year, older_threshold_time.month, older_threshold_time.day, 0, 0)
    vol_arr = []
    for volume_info in available_vol_response['Volumes']:
        s_create_time = datetime(
            volume_info['CreateTime'].year, volume_info['CreateTime'].month, volume_info['CreateTime'].day, 0, 0)
        try:

            vol = ec2_resource.Volume(id=volume_info['VolumeId'])
            name = None
            for tag in vol.tags:
                if tag['Key'] == 'Name':
                    name = tag.get('Value')
            if 'pvc' in name or 'kubernetes' in name:
                continue
        except:
            traceback.print_exc()

        if s_create_time < s_older_threshold_time:
            try:
                vol_arr.append(volume_info['VolumeId'] + ":" + str(
                    volume_info['Size']) + ":" + str(volume_info['CreateTime']))
            except Exception as e:
                debugPrint("Error Reported : " + str(e))

    if len(vol_arr) > 0:
        debugPrint("_##################  volumes in " + AWS_REGION + " / " + account_id +
                   " num which will be deleted older than " + str(days_count) + " days : " + str(len(vol_arr)))

    vol_arr.sort(reverse=True)
    for i in vol_arr:
        if delete_flag == "true":
            debugPrint("_Deleted Volume in " + AWS_REGION + " / " + account_id + " " + i.split(":")
                       [0] + " , Size :" + i.split(":")[1] + " , Creation Date :" + i.split(":")[2] + "_")
            #response = ec2_client.delete_volume(VolumeId=volume_info['VolumeId'])
        else:
            debugPrint("_Debug Deleted Volume in " + AWS_REGION + " / " + account_id + " " + i.split(
                ":")[0] + " , Size :" + i.split(":")[1] + " , Creation Date :" + i.split(":")[2] + "_")


def calculate_autoscaling_to_be_deleted(use_profile, AWS_REGION, account_id):
    if use_profile == "true":
        boto3.setup_default_session(profile_name='profile')

    client = boto3.client('autoscaling', region_name=AWS_REGION)
    autoscaler = client.describe_auto_scaling_groups()['AutoScalingGroups']
    autoscaler_arr = []
    for LC in autoscaler:
        if len(LC['Instances']) == 0:
            try:
                autoscaler_arr.append(LC['AutoScalingGroupName'] + ":" +
                                      str(len(LC['Instances'])) + ":" + str(LC['CreatedTime']))
            except:
                traceback.print_exc()

    if len(autoscaler_arr) > 0:
        debugPrint("_##################  Auto scaling group in " + AWS_REGION +
                   " / " + account_id + " num which will be deleted : " + str(len(autoscaler_arr)))

    autoscaler_arr.sort(reverse=True)
    for i in autoscaler_arr:
        debugPrint("_ASG in " + AWS_REGION + " / " + account_id + " " + i.split(":")[
            0] + " , Instance count :" + i.split(":")[1] + " , Creation Date :" + i.split(":")[2] + "_")


def calculate_autoscaling_instances_not_healty(use_profile, AWS_REGION, account_id):
    if use_profile == "true":
        boto3.setup_default_session(profile_name='profile')

    client = boto3.client('autoscaling', region_name=AWS_REGION)
    autoscaler = client.describe_auto_scaling_groups()['AutoScalingGroups']
    autoscaler_arr = []
    for LC in autoscaler:
        for ins in LC['Instances']:
            if 'HealthStatus' in ins:
                if ins['HealthStatus'] != 'Healthy':
                    skipFlag = True
                    print(int)
                    print('Found instance not healthy - skip ASG - ' +
                          ins['InstanceId'])
                    autoscaler_arr.append(ins['InstanceId'])
                    autoscaler_arr.append(
                        LC['AutoScalingGroupName'] + ":" + str(ins['InstanceId']))

    if len(autoscaler_arr) > 0:
        debugPrint("_##################  Auto scaling group in " + AWS_REGION +
                   " / " + account_id + " num which will be deleted : " + str(len(autoscaler_arr)))

    autoscaler_arr.sort(reverse=True)
    for i in autoscaler_arr:
        debugPrint("_ASG in " + AWS_REGION + " / " + account_id + " " + i)


def calculate_amis_to_be_deleted(use_profile, days_count, AWS_REGION, delete_flag, account_id):
    ami_age_limit = datetime.now() - timedelta(days=int(days_count))
    if use_profile == "true":
        boto3.setup_default_session(profile_name='profile')
    client = boto3.client('autoscaling', region_name=AWS_REGION)
    ec2_conn = boto3.client('ec2', region_name=AWS_REGION)

    response = client.describe_launch_configurations()
    launch_config_ami = []
    for LC in response['LaunchConfigurations']:
        launch_config_ami.append(LC['ImageId'])
    images_list = ec2_conn.describe_images(Owners=[account_id])
    images_list_arr_to_be_deleted = []
    len_images_list = len(images_list['Images'])
    for image in images_list['Images']:
        try:
            image_name = image['Name']
            image_id = image['ImageId']
            date_string = image['CreationDate']
            image_dt = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
            if image_dt < ami_age_limit:

                instances_list = ec2_conn.describe_instances(
                    Filters=[{'Name': 'image-id', 'Values': [image_id]}])
                active_reservations = instances_list['Reservations']
                if not active_reservations:
                    #                time.sleep(0.1)
                    print("in")
                    print(image_id)
                    images_list_arr_to_be_deleted.append(image_id)

        except:
            traceback.print_exc()
            pass

    #snapshots = ec2_conn.describe_snapshots(OwnerIds=[account_id])['Snapshots']
    if len(images_list_arr_to_be_deleted) > 0:
        debugPrint("_##################  Images in " + AWS_REGION + " / " + account_id + " are more than " + str(days_count) +
                   " days and not used by any instance #####_" + " , *num to delete* : " + str(len(images_list_arr_to_be_deleted)) + " from " + str(len_images_list))
    # exit(1)
    for i in images_list_arr_to_be_deleted:
        images_list = ec2_conn.describe_images(
            Filters=[{'Name': 'image-id', 'Values': [i]}])
        for image in images_list['Images']:
            if "ami" in image['ImageId']:
                time.sleep(0.1)
                if delete_flag == "true":
                    debugPrint("Deleted Image in " + AWS_REGION + " / " + account_id + ": CreationDate " + str(
                        image['CreationDate']) + ", Name " + str(image['Name']) + ", ImageId " + str(image['ImageId']))
                    # ec2_conn.deregister_image(ImageId=image['ImageId'])
                    for snapshot in snapshots:
                        if str(image['Name']) in snapshot['Description']:
                            #snap = ec.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
                            debugPrint("Deleted Snapshot in " + AWS_REGION + " / " + account_id + ": Snapshot Name " + str(
                                snapshot['Description']) + ", SnapshotID " + str(snapshot['SnapshotId']))
                else:
                    debugPrint("Debug Image in " + AWS_REGION + " / " + account_id + ":  CreationDate " + str(
                        image['CreationDate']) + ", Name " + str(image['Name']) + ", ImageId " + str(image['ImageId']))
                    for snapshot in snapshots:
                        if str(image['Name']) in snapshot['Description']:
                            debugPrint("Debug Image in " + AWS_REGION + " / " + account_id + ": Snapshot Name " + str(
                                snapshot['Description']) + ", SnapshotID " + str(snapshot['SnapshotId']))


def main(use_profile, regions_arr, days_count, delete_flag):

    client = boto3.client("sts")
    account_id = client.get_caller_identity()["Account"]

    for AWS_REGION in regions_arr:
        debugPrint("*################## Region ############# : " +
                   AWS_REGION + "*: Accoutn ID :" + account_id)
        time.sleep(0.1)
        calculate_volumes_to_be_deleted(
            use_profile, days_count, AWS_REGION, delete_flag, account_id)
        #calculate_autoscaling_to_be_deleted(use_profile, AWS_REGION, account_id)
        #calculate_autoscaling_instances_not_healty(use_profile, AWS_REGION, account_id)
        #calculate_amis_to_be_deleted(use_profile,days_count, AWS_REGION, delete_flag, account_id)


def lambda_handler(event, context):
    use_profile = os.environ['use_profile']
    debugPrint(use_profile)
    days_count = os.environ['days_count']
    debugPrint(days_count)
    regions_arr = os.environ['regions_arr'].split(",")
    debugPrint(regions_arr)
    delete_flag = os.environ['delete_flag']
    debugPrint(delete_flag)
    main(use_profile, regions_arr, days_count, delete_flag)
