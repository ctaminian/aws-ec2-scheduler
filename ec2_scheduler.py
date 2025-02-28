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
    print(f"\nStart time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}, Stop time: {stop_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Wait until start time
    wait_until_start_time(start_time, stop_time)

def wait_until_start_time(start_time, stop_time):
    """Wait until the start time, showing a countdown."""
    
    start_time = start_time.replace(microsecond=0)

    print(f"Waiting until {start_time.strftime('%Y-%m-%d %H:%M:%S')}...\n")

    now = datetime.now().replace(microsecond=0)
    
    while datetime.now().replace(microsecond=0) < start_time:
        time_remaining = (start_time - datetime.now()).total_seconds()
        print(f"Waiting for {int(time_remaining)} seconds...", end="\r")
        time.sleep(1)

    print("\n")
    print("Start time reached! Proceeding to launch EC2 instance...\n")

    # Launch the EC2 instance
    launch_ec2_instance(stop_time)

def launch_ec2_instance(stop_time):
    print("Launching EC2 instance...\n")
    
    wait_until_stop_time(stop_time)

def wait_until_stop_time(stop_time):
    stop_time = stop_time.replace(microsecond=0)

    now = datetime.now().replace(microsecond=0)
    
    while datetime.now().replace(microsecond=0) < stop_time:
        time_remaining = (stop_time - datetime.now()).total_seconds()
        print(f"Waiting for {int(time_remaining)} seconds...", end="\r")
        time.sleep(1)

    print("\n")
    print("Stop time reached! Proceeding to terminate the EC2 instance...\n")

# Function to get and validate start and stop times
def get_start_and_stop_times():
    print("Welcome to the EC2 Scheduler!")
    print("Please enter the start and stop times for the EC2 instance (HH:MM:SS format)\n")

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

            return start_time, stop_time

        except ValueError:
            print("Invalid format! Please enter time in HH:MM:SS.")


if __name__ == "__main__":
    main()