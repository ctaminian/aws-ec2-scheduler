import os
import boto3
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import fileinput
import botocore.exceptions

# Load environment variables from .env file
load_dotenv()

# Retrieve AWS credentials and settings from environment variables
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION")
AMI_ID = os.getenv("AMI_ID")
SECURITY_GROUP_ID = os.getenv("SECURITY_GROUP_ID")
INSTANCE_TYPE = os.getenv("INSTANCE_TYPE")

# Create an EC2 client
ec2 = boto3.client("ec2", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=AWS_REGION)
print("EC2 client created successfully\n")

def main():
    print("Welcome to the EC2 Scheduler!")
    launch_time, termination_time = get_launch_and_termination_times()
    wait_until_launch_time(launch_time, termination_time)

def wait_until_launch_time(launch_time, termination_time):
    launch_time = launch_time.replace(microsecond=0)

    print(f"Waiting until {launch_time.strftime('%Y-%m-%d %H:%M:%S')} to launch your EC2 instance...\n")

    while datetime.now().replace(microsecond=0) < launch_time:
        time_remaining = (launch_time - datetime.now()).total_seconds()
        print(f"Your EC2 instance is scheduled to launch in {int(time_remaining)} seconds...", end="\r")
        time.sleep(1)

    print("\nProceeding to launch your EC2 instance...\n")
    instance_id = launch_ec2_instance()
    
    if instance_id:
        wait_until_termination_time(instance_id, termination_time)

def launch_ec2_instance():
    print("Launching EC2 instance...\n")

    try:
        response = ec2.run_instances(ImageId=AMI_ID, InstanceType=INSTANCE_TYPE, MinCount=1, MaxCount=1, SecurityGroupIds=[SECURITY_GROUP_ID])
        instance_id = response["Instances"][0]["InstanceId"]
        print(f"EC2 Instance Launched: {instance_id}")

        ec2.get_waiter("instance_running").wait(InstanceIds=[instance_id])
        print(f"EC2 instance {instance_id} is now running.\n")

        update_env_file("EC2_INSTANCE_ID", instance_id)
        return instance_id

    except botocore.exceptions.ClientError as e:
        print(f"Error launching EC2 instance: {e}")
        return None

def wait_until_termination_time(instance_id, termination_time):
    termination_time = termination_time.replace(microsecond=0)

    print(f"Waiting until {termination_time.strftime('%Y-%m-%d %H:%M:%S')} to terminate your EC2 instance...\n")

    while datetime.now().replace(microsecond=0) < termination_time:
        time_remaining = (termination_time - datetime.now()).total_seconds()
        print(f"Your EC2 instance is scheduled to terminate in {int(time_remaining)} seconds...", end="\r")
        time.sleep(1)

    print("\nProceeding to terminate your EC2 instance...\n")
    terminate_ec2_instance(instance_id)

def terminate_ec2_instance(instance_id):
    if not instance_id:
        print("No running EC2 instance to terminate.")
        return

    try:
        print(f"Terminating EC2 instance {instance_id}...\n")
        ec2.terminate_instances(InstanceIds=[instance_id])

        ec2.get_waiter("instance_terminated").wait(InstanceIds=[instance_id])
        print(f"EC2 instance {instance_id} has been terminated.\n")

        update_env_file("EC2_INSTANCE_ID", "")
    except botocore.exceptions.ClientError as e:
        print(f"Error terminating EC2 instance: {e}")

def update_env_file(key, value):
    updated = False
    with fileinput.input(".env", inplace=True) as file:
        for line in file:
            if line.startswith(f"{key}="):
                print(f"{key}={value}")
                updated = True
            else:
                print(line, end="")

    if not updated:
        with open(".env", "a") as env_file:
            env_file.write(f"\n{key}={value}\n")

# Function to get and validate start and stop times
def get_launch_and_termination_times():
    print("Please enter the launch and termination times for the EC2 instance (HH:MM:SS format)\n")

    while True:
        try:
            launch_time_str = input("Launch time (HH:MM:SS): ")
            termination_time_str = input("Termination time (HH:MM:SS): ")
            print()

            now = datetime.now()

            # Parse input as today's date
            launch_time = datetime.strptime(launch_time_str, "%H:%M:%S").replace(
                year=now.year, month=now.month, day=now.day, microsecond=0
            )
            termination_time = datetime.strptime(termination_time_str, "%H:%M:%S").replace(
                year=now.year, month=now.month, day=now.day, microsecond=0
            )

            # Ensure AM/PM conversion aligns with system time
            if launch_time < now:
                if now.hour >= 12 and launch_time.hour < 12:
                    launch_time = launch_time.replace(hour=launch_time.hour + 12)
                    termination_time = termination_time.replace(hour=termination_time.hour + 12)
                else:
                    launch_time += timedelta(days=1)
                    termination_time += timedelta(days=1)
                    
            if termination_time <= launch_time:
                print("Termination time must be after start time. Try again.")
                continue

            return launch_time, termination_time

        except ValueError:
            print("Invalid format! Please enter time in HH:MM:SS.")

if __name__ == "__main__":
    main()