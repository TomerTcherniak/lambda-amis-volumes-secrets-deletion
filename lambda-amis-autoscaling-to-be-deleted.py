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



ec2_types = {}
ec2_running_instances = {}
ec2_reserved_instances = {}
rds_running_instances = {}
rds_reserved_instances = {}


def set_types():
    ec2_types.clear()
    ec2_running_instances.clear()
    ec2_reserved_instances.clear()
    rds_running_instances.clear()
    rds_reserved_instances.clear()


class Slack(object):
    def __init__(self):
        self.slackurl = "https://hooks.slack.com/services/ChangeME"
        self.iconemoji = ":coin:"
        self.slackusername = "AMI Deletion / Reservation info"

    def set_slackurl(self, url):
        self.slackurl = url

    def post_data(self, message, headers={'Content-Type': 'application/json'}):
        print(message)
        values = {"username": self.slackusername,
                  "text": message, "icon_emoji": self.iconemoji}
        params = json.dumps(values).encode('utf8')
        req = request.Request(self.slackurl, params, headers)
        resp = request.urlopen(req)


def calculate_volumes_to_be_deleted(use_profile,days_count, AWS_REGION, delete_flag, account_id):
    slackObject = Slack()
    if use_profile == "true":
        boto3.setup_default_session(profile_name='profile')

    ec2_client = boto3.client('ec2', region_name=AWS_REGION)
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
    older_threshold_time ='{0.month}/{0.day}/{0.year} {0.hour}:{0.minute}'.format(older_threshold_time)
    vol_arr = []
    for volume_info in available_vol_response['Volumes']:
        create_time = '{0.month}/{0.day}/{0.year} {0.hour}:{0.minute}'.format(volume_info['CreateTime'])
        if  create_time < older_threshold_time:
            try:
                vol_arr.append(volume_info['VolumeId'] + ":" + str(volume_info['Size']) + ":" + str(volume_info['CreateTime']))
            except Exception as e:
                print("Error Reported : " + str(e))

    if len(vol_arr) > 0:
        slackObject.post_data("_##################  volumes in " + AWS_REGION +
                              " / " + account_id + " num which will be deleted older than " + str(days_count) + " days : " + str(len(vol_arr)))

    vol_arr.sort(reverse=True)
    for i in vol_arr:
        if delete_flag == "true":
            slackObject.post_data("_Deleted Volume in " + AWS_REGION + " / " + account_id + " " +  i.split(":")[
                                  0] + " , Size :" + i.split(":")[1] + " , Creation Date :" + i.split(":")[2] + "_")
            response = ec2_client.delete_volume(VolumeId=volume_info['VolumeId'])
        else:
            slackObject.post_data("_Debug Deleted Volume in " + AWS_REGION + " / " + account_id + " " + i.split(":")[
                                  0] + " , Size :" + i.split(":")[1] + " , Creation Date :" + i.split(":")[2] + "_")


def calculate_autoscaling_to_be_deleted(use_profile, AWS_REGION, account_id):
    slackObject = Slack()
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
        slackObject.post_data("_##################  Auto scaling group in " + AWS_REGION +
                              " / " + account_id + " num which will be deleted : " + str(len(autoscaler_arr)))

    autoscaler_arr.sort(reverse=True)
    for i in autoscaler_arr:
        slackObject.post_data("_ASG in " + AWS_REGION + " / " + account_id + " " + i.split(":")[
                              0] + " , Instance count :" + i.split(":")[1] + " , Creation Date :" + i.split(":")[2] + "_")


def calculate_amis_to_be_deleted(use_profile, days_count, AWS_REGION, delete_flag, account_id):
    ami_age_limit = datetime.now() - timedelta(days=int(days_count))
    slackObject = Slack()
    if use_profile == "true":
        boto3.setup_default_session(profile_name='profile')
    client = boto3.client('autoscaling', region_name=AWS_REGION)
    response = client.describe_launch_configurations()
    launch_config_ami = []
    for LC in response['LaunchConfigurations']:
        launch_config_ami.append(LC['ImageId'])
    ec2_conn = boto3.client('ec2', region_name=AWS_REGION)
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
                    time.sleep(0.1)
                    if image_id not in launch_config_ami:
                        images_list_arr_to_be_deleted.append(image_id)

        except:
            pass

    snapshots = ec2_conn.describe_snapshots(
        OwnerIds=[account_id])['Snapshots']
    if len(images_list_arr_to_be_deleted) > 0:
        slackObject.post_data("_##################  Images in " + AWS_REGION + " / " + account_id + " are more than " + str(days_count) +
                              " days and not used by any instance #####_" + " , *num to delete* : " + str(len(images_list_arr_to_be_deleted)) + " from " + str(len_images_list))

    for i in images_list_arr_to_be_deleted:
        images_list = ec2_conn.describe_images(
            Filters=[{'Name': 'image-id', 'Values': [i]}])
        for image in images_list['Images']:
            if "ami" in image['ImageId']:
                time.sleep(0.1)
                if delete_flag == "true":
                    slackObject.post_data("Deleted Image in " + AWS_REGION + " / " + account_id + ": CreationDate " + str(
                        image['CreationDate']) + ", Name " + str(image['Name']) + ", ImageId " + str(image['ImageId']))
                    ec2_conn.deregister_image(ImageId=image['ImageId'])
                    for snapshot in snapshots:
                        if str(image['Name']) in snapshot['Description']:
                            snap = ec.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
                            slackObject.post_data("Deleted Snapshot in " + AWS_REGION + " / " + account_id + ": Snapshot Name " + str(
                                snapshot['Description']) + ", SnapshotID " + str(snapshot['SnapshotId']))
                else:
                    slackObject.post_data("Debug Image in " + AWS_REGION + " / " + account_id + ":  CreationDate " + str(
                        image['CreationDate']) + ", Name " + str(image['Name']) + ", ImageId " + str(image['ImageId']))
                    for snapshot in snapshots:
                        if str(image['Name']) in snapshot['Description']:
                            slackObject.post_data("Debug Image in " + AWS_REGION + " / " + account_id + ": Snapshot Name " + str(
                                snapshot['Description']) + ", SnapshotID " + str(snapshot['SnapshotId']))


def calculate_rds_ris(use_profile, region, rds_or_ec2):
    if use_profile == "true":
        print("using profile...")
        boto3.setup_default_session(profile_name='profile')
    rds_conn = boto3.client('rds', region_name=region)
    paginator = rds_conn.get_paginator('describe_db_instances')
    page_iterator = paginator.paginate()

    for page in page_iterator:
        for instance in page['DBInstances']:
            instance_type = instance['DBInstanceClass']
            instance_type = instance_type.split(".")[1]
            rds_running_instances[(instance_type)] = rds_running_instances.get(
                instance_type, 0) + 1

    paginator = rds_conn.get_paginator('describe_reserved_db_instances')
    page_iterator = paginator.paginate()

    # Loop through active RDS RIs and record their type and Multi-AZ setting.
    for page in page_iterator:
        for reserved_instance in page['ReservedDBInstances']:
            if reserved_instance['State'] == 'active':
                instance_type = reserved_instance['DBInstanceClass']
                instance_type = instance_type.split(".")[1]
                rds_reserved_instances[(instance_type)] = rds_reserved_instances.get(
                    instance_type, 0) + 1


def calculate_ec2_ris(use_profile, region, rds_or_ec2):
    slackObject = Slack()
    if use_profile == "true":
        boto3.setup_default_session(profile_name='profile')
    ec2_conn = boto3.client('ec2', region_name=region)
    paginator = ec2_conn.get_paginator('describe_instances')
    page_iterator = paginator.paginate(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

    for reserved_instance in ec2_conn.describe_reserved_instances()['ReservedInstances']:
        if reserved_instance['State'] == "active":
            instance_type = reserved_instance['InstanceType']
            instance_type = instance_type.split(".")[0]
            end = reserved_instance['End']
            if reserved_instance['Scope'] == 'Availability Zone':
                az = reserved_instance['AvailabilityZone']
            else:
                az = 'All'
            ec2_reserved_instances[(instance_type)] = ec2_reserved_instances.get(
                (instance_type), 0) + reserved_instance['InstanceCount']
            #lt_delta=end - datetime.datetime.now(end.tzinfo)
            lt_delta = end - datetime.now(end.tzinfo)
            if (int(lt_delta.days) < 90):
                msg = "Less than 90 days for reservation {instance_type}  , days left {days} ,state {State} ,instance count {InstanceCount}".format(
                    instance_type=instance_type, days=str(lt_delta.days), State=str(reserved_instance['State']), InstanceCount=str(reserved_instance['InstanceCount']))
                slackObject.post_data(
                    region + " #  " + rds_or_ec2 + " # " + msg)

            if ec2_types.get(instance_type) == None:
                ec2_types[instance_type] = 1
    for page in page_iterator:
        for reservation in page['Reservations']:
            for instance in reservation['Instances']:
                if 'SpotInstanceRequestId' not in instance:
                    az = instance['Placement']['AvailabilityZone']
                    instance_type = instance['InstanceType']
                    instance_type = instance_type.split(".")[0]
                    ec2_running_instances[(instance_type)] = ec2_running_instances.get(
                        (instance_type), 0) + 1


def check_reserved_instances(region_name, running_instances, reserved_instances, rds_or_ec2):
    slackObject = Slack()
    sort_reserved_instances = sorted(
        reserved_instances.items(), key=operator.itemgetter(0))
    dict_sort_reserved_instances = dict(sort_reserved_instances)
    for k, v in sorted(dict_sort_reserved_instances.items()):
        try:
            print(running_instances[k])
        except:
            msg = "***** NoneRunningInstancesReserved : Type {v}, Reserved : {reserved_instances} *** ".format(
                v=str(k), reserved_instances=str(reserved_instances[k]))
            slackObject.post_data(+ "\n>" + region_name +
                                  " # " + rds_or_ec2 + " # " + msg + "\n>")

    sort_ec2_running_instances = sorted(
        running_instances.items(), key=operator.itemgetter(0))
    dict_sort_ec2_running_instances = dict(sort_ec2_running_instances)

    for k, v in sorted(dict_sort_ec2_running_instances.items()):
        try:
            time.sleep(0.1)
            if k is not None and v is not None:
                if running_instances[k] is not None and reserved_instances[k] is not None:
                    if int(running_instances[k] - reserved_instances[k]) > 0:
                        msg = "UnderReserved : {k} ,Running : {running_instances}  ,Reserved : {reserved_instances} ,Diff :{diff}".format(k=k, running_instances=str(
                            running_instances[k]), reserved_instances=str(reserved_instances[k]), diff=str(running_instances[k] - reserved_instances[k]))
                    if int(running_instances[k] - reserved_instances[k]) < 0:
                        msg = "**** NotUsed : {k} ,Running : {running_instances}  ,Reserved : {reserved_instances} ,Diff :{diff} ****".format(k=k, running_instances=str(
                            running_instances[k]), reserved_instances=str(reserved_instances[k]), diff=str(running_instances[k] - reserved_instances[k]))
                    if int(running_instances[k] - reserved_instances[k]) == 0:
                        msg = "Equal : {k} ,Running : {running_instances}  ,Reserved : {reserved_instances} ,Diff :{diff}".format(k=k, running_instances=str(
                            running_instances[k]), reserved_instances=str(reserved_instances[k]), diff=str(running_instances[k] - reserved_instances[k]))
                slackObject.post_data(
                    region_name + " # " + rds_or_ec2 + " # " + msg)
        except:
            try:
                if running_instances[k] is not None:
                    msg = "NoneReserved : Type {v}, Running : {running_instances} ".format(
                        v=str(k), running_instances=str(running_instances[k]))
                    slackObject.post_data(
                        region_name + " # " + rds_or_ec2 + " # " + msg)
                    continue
            except:
                msg = "NoneReserved : Type {v}".format(v=str(k))
                slackObject.post_data(
                    region_name + " # " + rds_or_ec2 + " # " + msg)


def main(use_profile, regions_arr, days_count, delete_flag):
    slackObject = Slack()

    client = boto3.client("sts")
    account_id = client.get_caller_identity()["Account"]

    for AWS_REGION in regions_arr:
        slackObject.post_data("*################## Region ############# : " +
                              AWS_REGION + "*: Accoutn ID :" + account_id)
        for rds_or_ec2 in ["ec2 "]:
            time.sleep(0.1)
            set_types()
            if rds_or_ec2 in "rds":
                calculate_rds_ris(use_profile, AWS_REGION, rds_or_ec2)
                check_reserved_instances(
                    AWS_REGION, rds_running_instances, rds_reserved_instances, rds_or_ec2)
            else:
                calculate_ec2_ris(use_profile, AWS_REGION, rds_or_ec2)
                check_reserved_instances(
                    AWS_REGION, ec2_running_instances, ec2_reserved_instances, rds_or_ec2)

        time.sleep(0.1)
        calculate_amis_to_be_deleted(
            use_profile, days_count, AWS_REGION, delete_flag, account_id)

        time.sleep(0.1)
        calculate_autoscaling_to_be_deleted(
            use_profile, AWS_REGION, account_id)

        time.sleep(0.1)
        calculate_volumes_to_be_deleted(
            use_profile,days_count, AWS_REGION, delete_flag, account_id)

def lambda_handler(event, context):
    use_profile = os.environ['use_profile']
    print(use_profile)
    days_count = os.environ['days_count']
    print(days_count)
    regions_arr = str(os.environ['regions_arr']).split(",")
    print(regions_arr)
    delete_flag = os.environ['delete_flag']
    print(delete_flag)
    main(use_profile, regions_arr, days_count, delete_flag)
