import os
import boto3
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve AWS credentials, region, and EC2 instance ID from environment variables
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
    print(f"✅ Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}, Stop time: {stop_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Wait until start time
    wait_until_start_time(start_time)

def wait_until_start_time(start_time):
    """Wait until the start time, showing a countdown."""
    
    start_time = start_time.replace(microsecond=0)

    print(f"⏳ Waiting until {start_time.strftime('%Y-%m-%d %H:%M:%S')}...")

    now = datetime.now().replace(microsecond=0)
    
    while datetime.now().replace(microsecond=0) < start_time:
        time_remaining = (start_time - datetime.now()).total_seconds()
        print(f"⏳ Waiting for {int(time_remaining)} seconds...", end="\r")
        time.sleep(1)

    print("\n🚀 Start time reached! Proceeding to launch EC2 instance...")

# Function to get and validate start and stop times
def get_start_and_stop_times():
    print("Welcome to the EC2 Scheduler!")
    print("Please enter the start and stop times for the EC2 instance (HH:MM:SS format)")

    while True:
        try:
            start_time_str = input("Start time (HH:MM:SS): ")
            stop_time_str = input("Stop time (HH:MM:SS): ")

            now = datetime.now()

            # Parse input as today's date
            start_time = datetime.strptime(start_time_str, "%H:%M:%S").replace(
                year=now.year, month=now.month, day=now.day, microsecond=0
            )
            stop_time = datetime.strptime(stop_time_str, "%H:%M:%S").replace(
                year=now.year, month=now.month, day=now.day, microsecond=0
            )

            # Ensure AM/PM conversion aligns with system time
            if start_time < now:
                if now.hour >= 12 and start_time.hour < 12:
                    start_time = start_time.replace(hour=start_time.hour + 12)
                    stop_time = stop_time.replace(hour=stop_time.hour + 12)
                else:
                    start_time += timedelta(days=1)
                    stop_time += timedelta(days=1)
                    
            if stop_time <= start_time:
                print("Stop time must be after start time. Try again.")
                continue

            return start_time, stop_time  # Return valid times

        except ValueError:
            print("❌ Invalid format! Please enter time in HH:MM:SS.")

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