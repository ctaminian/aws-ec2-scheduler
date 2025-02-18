import os
import boto3
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve AWS credentials, region and ec2 instance id from environment variables
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION")
EC2_INSTANCE_ID = os.getenv("EC2_INSTANCE_ID")

# Create an EC2 client
ec2 = boto3.client("ec2", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=AWS_REGION)
print("EC2 client created successfully")

def main():
    # Call of the describe instance function
    describe_instance()

def describe_instance():
    print("Describing EC2 instance...\n")
    # Describe the instance
    response = ec2.describe_instances(InstanceIds=[EC2_INSTANCE_ID])

    # Extract instance details
    instance = response["Reservations"][0]["Instances"][0]

    # Get key details of the instance
    print("Key details of the instance:")
    instance_id = instance["InstanceId"]
    instance_state = instance["State"]["Name"]
    instance_type = instance["InstanceType"]
    public_ip = instance.get("PublicIpAddress", "No Public IP")

    # Print instance details
    print(f"Instance ID: {instance_id}")
    print(f"Instance State: {instance_state}")
    print(f"Instance Type: {instance_type}")
    print(f"Public IP: {public_ip}")

if __name__ == "__main__":
    main()