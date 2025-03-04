import os
import boto3
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve AWS credentials, region, and EC2 AMI ID and Security Group ID from environment variables
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION")
AMI_ID = os.getenv("AMI_ID")
SECURITY_GROUP_ID = os.getenv("SECURITY_GROUP_ID")
INSTANCE_TYPE = os.getenv("INSTANCE_TYPE")
EC2_INSTANCE_ID = None

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

    now = datetime.now().replace(microsecond=0)
    
    while datetime.now().replace(microsecond=0) < launch_time:
        time_remaining = (launch_time - datetime.now()).total_seconds()
        print(f"Your EC2 instance is scheduled to launch in {int(time_remaining)} seconds...", end="\r")
        time.sleep(1)

    print("\n")
    print("Proceeding to launch your EC2 instance...\n")

    # Launch the EC2 instance
    launch_ec2_instance(termination_time)

def launch_ec2_instance(termination_time):
    print("Launching EC2 instance...\n")
    
    response = ec2.run_instances(ImageId=AMI_ID, InstanceType=INSTANCE_TYPE, MinCount=1, MaxCount=1, SecurityGroupIds=[SECURITY_GROUP_ID])

    global EC2_INSTANCE_ID
    EC2_INSTANCE_ID = response["Instances"][0]["InstanceId"]
    print(f"EC2 Instance Launched: {EC2_INSTANCE_ID}")

    ec2.get_waiter("instance_running").wait(InstanceIds=[EC2_INSTANCE_ID])
    print(f"EC2 instance {EC2_INSTANCE_ID} is now running.\n")

    env_path = ".env"

    with open(".env", "r") as env_file:
        lines = env_file.readlines()

    key_found = False
    with open(".env", "w") as env_file:
        for line in lines:
            if line.startswith("EC2_INSTANCE_ID="):
                env_file.write(f"EC2_INSTANCE_ID={EC2_INSTANCE_ID}\n")
                key_found = True
            else:
                env_file.write(line)

        if not key_found:
            env_file.write(f"EC2_INSTANCE_ID={EC2_INSTANCE_ID}\n")

    wait_until_termination_time(termination_time)

def wait_until_termination_time(termination_time):
    termination_time = termination_time.replace(microsecond=0)

    print(f"Waiting until {termination_time.strftime('%Y-%m-%d %H:%M:%S')} to terminate your EC2 instance...\n")

    now = datetime.now().replace(microsecond=0)
    
    while datetime.now().replace(microsecond=0) < termination_time:
        time_remaining = (termination_time - datetime.now()).total_seconds()
        print(f"Your EC2 instance is scheduled to terminate in {int(time_remaining)} seconds...", end="\r")
        time.sleep(1)

    print("\n")
    print("Proceeding to terminate your EC2 instance...\n")

    # Terminate the EC2 instance
    terminate_ec2_instance()

def terminate_ec2_instance():
    print("Terminating EC2 instance...\n")

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