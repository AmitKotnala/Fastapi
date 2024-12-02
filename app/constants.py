import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = "postgresql+psycopg2://{}:{}@{}/{}".format(
    os.getenv("DATABASE_USER"),
    os.getenv("DATABASE_PASS"),
    os.getenv("DATABASE_URL"),
    os.getenv("DATABASE_DB"),
)

LOCAL_S3 = os.getenv('LOCAL_S3')

# JWT Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Email Verification
VERIFICATION_TOKEN_EXPIRE_MINUTES = 30

# AWS S3 Configuration
AWS_CLIENT_ID = os.getenv('AWS_CLIENT_ID')
AWS_CLIENT_KEY = os.getenv('AWS_CLIENT_KEY')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')
AWS_REGION = 'us-east-1'

# File Upload Configurations
ALLOWED_FILE_EXTENSIONS = ['.pptx', '.docx', '.xlsx']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

print(DATABASE_URL)
print(AWS_CLIENT_ID,'\n',AWS_CLIENT_KEY,'\n',AWS_BUCKET_NAME)