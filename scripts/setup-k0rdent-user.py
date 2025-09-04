#!/usr/bin/env python3

import argparse
import boto3
import sys
from botocore.exceptions import ClientError
import subprocess
import os


STAK_NAME = "cluster-api-provider-aws-sigs-k8s-io"
ROLE = "control-plane.cluster-api-provider-aws.sigs.k8s.io"


def get_aws_region() -> str:
    aws_region = os.getenv("AWS_REGION")
    if aws_region == None:
        raise Exception(f"AWS_REGION environment variable not found, please set!")
    return aws_region


def user_exits(username: str) -> bool:
    iam = boto3.client("iam")
    try:
        iam.get_user(UserName=username)
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchEntity":
            return False
        raise e
    return True


def ensure_user(username: str):
    if user_exits(username=username):
        print(f"IAM user '{username}' already exists.")
        return
    iam = boto3.client("iam")
    iam.create_user(UserName=username)
    print(f"IAM user '{username}' created successfully.")


def stack_exists(aws_region: str) -> bool:
    cfn = boto3.client("cloudformation", region_name=aws_region)
    try:
        cfn.describe_stack_resources(StackName=STAK_NAME)
    except ClientError as e:
        if e.response["ResponseMetadata"]["HTTPStatusCode"] == 400:
            return False
        raise e
    return True


def role_exists() -> bool:
    iam = boto3.client("iam")
    try:
        iam.get_role(RoleName=ROLE)
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchEntity":
            return False
        raise e
    return True


def detect_stack_region(aws_region: str) -> str:
    ec2 = boto3.client("ec2", region_name=aws_region)
    regions = [r["RegionName"] for r in ec2.describe_regions()["Regions"]]
    for region in regions:
        if stack_exists(region):
            return region
    raise Exception("AWS region of the existing stack not found!")


def ensure_stack(aws_region: str):
    if stack_exists(aws_region):
        print(f"Stack '{STAK_NAME}' already exists. Trying to update...")
    elif role_exists():
        print(f"Error: Stack '{STAK_NAME}' not found in used AWS region ({aws_region}), "+
              f"but stack role '{ROLE}' found! There is probably the stack created in a different region. "+
              "Trying to locate existing CloudFormation stack...")
        detected_region = detect_stack_region(aws_region)
        raise Exception(f"Conflicting stack ({STAK_NAME}) found in '{detected_region}'. Please, use this region.")
    subprocess.run(["clusterawsadm", "bootstrap", "iam", "create-cloudformation-stack", "--region", aws_region], check=True)


def get_policies(aws_region: str) -> list:
    policies = []
    cfn = boto3.client("cloudformation", region_name=aws_region)
    resources = cfn.describe_stack_resources(StackName=STAK_NAME)
    for res in resources["StackResources"]:
        if res["ResourceType"] == "AWS::IAM::ManagedPolicy":
            policies.append(res["PhysicalResourceId"])
    return policies


def attach_policies(policies: list, username: str):
    iam = boto3.client("iam")
    for policy in policies:
        iam.attach_user_policy(UserName=username, PolicyArn=policy)
        print(f"Policy '{policy}' attached to user '{username}'")


def create_access_key(username: str, output_file_path: str):
    iam = boto3.client("iam")
    response = iam.create_access_key(UserName=username)
    access_key = response["AccessKey"]
    print("----")
    print(f"Access key created successfully for IAM user '{username}'")
    print(f"Access Key ID: {access_key['AccessKeyId']}")
    export_aws_secrets(access_key['AccessKeyId'], access_key['SecretAccessKey'], output_file_path)


def export_aws_secrets(access_key_id: str, secret_access_key: str, filepath: str):
    data = f"""
# AWS k0rdent provider
export AWS_ACCESS_KEY_ID_USER="{access_key_id}"
export AWS_SECRET_ACCESS_KEY_USER="{secret_access_key}"
"""
    with open(filepath, mode="w", encoding="utf-8") as f:
        f.write(data)


parser = argparse.ArgumentParser(
    description="Create an IAM user with the given username"
)
parser.add_argument(
    "username",
    help="Name of the IAM user to create"
)
parser.add_argument(
    "output_secrets_file",
    help="File path to export k0rdent user secrets"
)
args = parser.parse_args()

try:
    aws_region = get_aws_region()
    ensure_stack(aws_region)
    user_arn = ensure_user(args.username)
    policies = get_policies(aws_region)
    attach_policies(policies, args.username)
    create_access_key(args.username, args.output_secrets_file)
except Exception as e:
    print("ERROR:", e)
    sys.exit(1)
