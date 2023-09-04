import os
from google.cloud import storage
from google_services.authorization.get_oauth_creds import get_creds
from config import GOOGLE_PROJECT_ID
import requests
import json

def create_bucket(
        bucket_name:str,
        location: str=None,
        project_id: str=GOOGLE_PROJECT_ID
        ):
    
    creds = get_creds()
    storage_client = storage.Client(credentials=creds, project=project_id)
    
    bucket = storage_client.bucket(bucket_name)
    if location:
        bucket.create(location=location)

    return bucket

def upload_file_to_bucket(
        blob_relative_path: str,
        file_path: str,
        bucket_name: str,
        project_id: str=GOOGLE_PROJECT_ID
        ):
    
    creds = get_creds()
    storage_client = storage.Client(credentials=creds, project=project_id)
    
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_relative_path)
    blob.upload_from_filename(file_path, timeout=600)
    blob.gs_uri = f"gs://{bucket_name}/{blob_relative_path}"

    print(f'Successfully uploaded {blob_relative_path} to GCS.')
    
    return blob

def get_bucket_data(bucket_object) -> dict:
    
    bucket_data = vars(bucket_object)
    print(bucket_data)
    
    return bucket_data


def delete_bucket(bucket_name: str):
    '''
    curl -X DELETE -H "Authorization: Bearer OAUTH2_TOKEN" \
    "https://storage.googleapis.com/storage/v1/b/BUCKET_NAME"
    '''
    creds = get_creds()
    token = creds.token

    headers = {"Authorization": f"Bearer {token}"}
    req_url = f"https://storage.googleapis.com/storage/v1/b/{bucket_name}" 
    req = requests.delete(url=req_url, headers=headers)
    if req.content:
        message = json.loads(req.content)
        print(f'Message: {message}')
    
    if req.status_code == 204:
        print(f"Successfully deleted bucket: {bucket_name}")


    return req.status_code

def list_bucket_files(bucket_name: str, project_id: str=GOOGLE_PROJECT_ID):
    """Lists all files(blobs) in a bucket of a certain project_id """
    creds = get_creds()
    storage_client = storage.Client(credentials=creds, project=project_id)
    blobs = storage_client.list_blobs(bucket_name)
    for blob in blobs:
        print(blob.name)
    
    return blobs

def delete_blob(bucket_name: str, blob_name: str, project_id: str=GOOGLE_PROJECT_ID):
    """Deletes a blob from the bucket."""
    creds = get_creds()
    storage_client = storage.Client(credentials=creds, project=project_id)

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()

    print(f"Blob {blob_name} deleted.")

def delete_nonempty_bucket(bucket_name: str, project_id: str=GOOGLE_PROJECT_ID):
    """Deletes a bucket with all files in that"""
    creds = get_creds()
    storage_client = storage.Client(credentials=creds, project=project_id)
    blobs = storage_client.list_blobs(bucket_name)
    
    for idx, blob in enumerate(blobs, start=1):
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob.name)
        blob.delete()
        print(f"#{idx}. Successfully deleted blob: {blob.name}")
    
    print(f"All files deleted from bucket: {bucket_name}. Now deleting the bucket itself.")

    delete_bucket(bucket_name)

    return None

if __name__ == '__main__':
    main_bucket = "no-war-poem-bucket"
    files = list_bucket_files(main_bucket)

    delete_nonempty_bucket(main_bucket)

    bucket_name = 'no-war-poem-test-bucket'
    bucket_for_del = "bucket_to_delete_vk"
    
    bucket_obj = create_bucket(bucket_for_del, location='Asia')
    delete_bucket(bucket_for_del)
    

    file_paths = ["speech_to_text_glitch/output/full_new_year_speech_putin.flac"]
    for path in file_paths:
        file_name = path.split('/')[-1]
        upload_file_to_bucket(file_name, path, bucket_name)
    
    print('Hello world!')