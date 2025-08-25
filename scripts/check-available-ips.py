#!/usr/bin/env python3

import argparse
import boto3
import sys

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Check available Elastic IPs in a specific AWS region"
    )
    parser.add_argument(
        "--aws-region",
        default="eu-central-1",
        help="AWS region to check (e.g. us-east-1)"
    )
    args = parser.parse_args()

    try:
        # Create an EC2 client for the specified region
        ec2 = boto3.client('ec2', region_name=args.aws_region)

        # Get the account's Elastic IP limit
        attributes = ec2.describe_account_attributes(
            AttributeNames=['vpc-max-elastic-ips']
        )
        limit = int(attributes['AccountAttributes'][0]['AttributeValues'][0]['AttributeValue'])

        # Get the number of allocated Elastic IPs
        addresses = ec2.describe_addresses()
        used = len(addresses['Addresses'])

        # Calculate available Elastic IPs
        available = limit - used

        print(f"Region: {args.aws_region}")
        print(f"Elastic IP Limit: {limit}")
        print(f"Elastic IPs Used: {used}")
        print(f"Available Elastic IPs: {available}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
