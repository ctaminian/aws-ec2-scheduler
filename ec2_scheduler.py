import os
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWSA_REGION = os.getenv("AWS_DEFAULT_REGION")

print("AWS Keys Loaded Successfully")