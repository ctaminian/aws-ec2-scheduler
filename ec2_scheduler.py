import os
import boto3
import time
from datetime import datetime
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
print("EC2 client created successfully\n")

def main():

    # Get start and stop times from the user
    start_time, stop_time = get_start_and_stop_times()
    print(f"✅ Start time: {start_time.strftime('%H:%M:%S')}, Stop time: {stop_time.strftime('%H:%M:%S')}")

# Function to display the main menu and handle user input
def get_start_and_stop_times():
    print("Welcome to the EC2 Scheduler!")
    print("Please enter the start and stop times for the EC2 instance (in HH:MM:SS format)")
    
    while True:
        try:
            start_time_str = input("Start time: ")
            stop_time_str = input("Stop time: ")

            now = datetime.now()
            start_time = datetime.strptime(start_time_str, "%H:%M:%S").replace(year=now.year, month=now.month, day=now.day)
            stop_time = datetime.strptime(stop_time_str, "%H:%M:%S").replace(year=now.year, month=now.month, day=now.day)

            if stop_time <= start_time:
                print("Stop time must be after start time. Try again.")
                continue

            return start_time, stop_time

        except ValueError:
            print("Invalid time format. Please enter the time in HH:MM:SS format.")

# Function to start the EC2 instance
def start_instance():
    print("Starting EC2 instance...\n")
    ec2.start_instances(InstanceIds=[EC2_INSTANCE_ID])
    print("EC2 instance started successfully\n")

# Function to stop the EC2 instance
def stop_instance():
    print("Stopping EC2 instance...\n")
    ec2.stop_instances(InstanceIds=[EC2_INSTANCE_ID])
    print("EC2 instance stopped successfully\n")

# Function to describe the EC2 instance
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
    print(f"Public IP: {public_ip}\n")

if __name__ == "__main__":
    main()