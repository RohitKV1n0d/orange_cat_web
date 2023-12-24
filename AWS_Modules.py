import boto3
import os
import uuid

AWS_ACCESS_KEY_ID=os.environ.get('CLOUDCUBE_ACCESS_KEY_ID') #os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRECT_ACCESS_KEY=os.environ.get('CLOUDCUBE_SECRET_ACCESS_KEY') # os.environ.get('AWS_SECRECT_ACCESS_KEY')
BUCKET_NAME=os.environ.get('BUCKET_NAME')
S3_ENDPOINT=os.environ.get('BUCKET_URL')
REGION_NAME=os.environ.get('REGION_NAME')

# Create a new SES resource and specify a region.
s3 = boto3.client('s3',region_name=REGION_NAME, aws_access_key_id=AWS_ACCESS_KEY_ID,  
            aws_secret_access_key= AWS_SECRECT_ACCESS_KEY)


def upload_file_to_s3(file, bucket, object_name=None, public=True):
    """Upload a file to an S3 bucket

    :param file: File to upload
    :param bucket: Bucket to upload to
    
    :param object_name: S3 object name. If not specified then file is used
    :param public: True if public, False if private
    :return: True if file was uploaded, else False
    """
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = uuid.uuid4().hex + '.jpeg'
    
    # Upload the file
    try:
        s3_path = 'lu3eeh4bls8g/public/' if public else 'lu3eeh4bls8g/'
        s3.upload_file(file, bucket, s3_path + object_name)
        url = f'https://{BUCKET_NAME}.s3.amazonaws.com/{s3_path}{object_name}'
    except Exception as e:
        print("Error in upload_file_to_s3: ", e)
        return False
    
    return url

def delete_file_from_s3(file_name, bucket, public=True):
    """Delete a file from an S3 bucket

    :param file_name: File to delete
    :param bucket: Bucket to delete from
    
    :param public: True if public, False if private
    :return: True if file was deleted, else False
    """
    # Upload the file
    try:
        s3_path = 'lu3eeh4bls8g/public/' if public else 'lu3eeh4bls8g/'
        s3.delete_object(Bucket=bucket, Key=s3_path + file_name)
    except Exception as e:
        print(e)
        return False
    
    print('File deleted successfully')
    return True


